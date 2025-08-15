# BoulderBot_Offline_Smart.py
# Features:
# - /mode coach|safety|competition
# - Personalized local profile per user (preferences, history)
# - Weighted retrieval (exact phrase, keyword overlap, mode-topic match)
# - Cleaned DeepSeek output (hides "thinking")
# - Fun loading animation

# Usage tips

# Switch modes anytime: /mode coach, /mode safety, /mode competition

# Personalize: /set goal: send V5 on overhang, /add style: slab, /add weakness: crimps

# View profile: /profile


import json, os, re, sys, time, threading, subprocess
from pathlib import Path
from collections import Counter, defaultdict

# -------------------------- Config --------------------------
KB_PATHS = [
    "bouldering_dataset.json",        # your Q&A dataset: {topic, level, question, answer}
    "bouldering_tips.json"            # optional tips: {id, tip, difficulty, category}
]
MODEL_NAME = "deepseek-r1:8b"
TOP_K_CONTEXT = 6                    # how many top context items to pass to the model
PROFILE_DIR = Path("./profiles")
PROFILE_DIR.mkdir(exist_ok=True)

MODE = "coach"                       # default: coach|safety|competition
MODE_TOPIC_MAP = {
    "coach": {"Training", "Technique", "Route Reading", "Grip Technique"},
    "safety": {"Safety", "Injury Prevention"},
    "competition": {"Competition", "Mindset"}
}

# Keep responses crisp
SYSTEM_STYLE = (
    "You are a friendly, expert bouldering coach. "
    "Give concise, actionable advice with clear steps. "
    "Prefer 3–6 short bullet points or 2–4 short paragraphs. "
    "Avoid rambling, avoid speculation, and include safety notes when relevant."
)

# -------------------------- Utils --------------------------
def load_kb():
    items = []
    for p in KB_PATHS:
        if not Path(p).exists():
            continue
        with open(p, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue
        # Normalize to a common schema
        for e in data:
            topic = e.get("topic") or e.get("category") or "General"
            level = e.get("level") or e.get("difficulty") or ""
            if "question" in e and "answer" in e:
                text = f"Q: {e['question']}\nA: {e['answer']}"
                q = e["question"]
            else:
                tip = e.get("tip") or ""
                text = tip
                q = tip
            items.append({
                "topic": topic,
                "level": level,
                "q": q,
                "text": text
            })
    return items

KB = load_kb()

def tokenize(s: str):
    return re.findall(r"[a-z0-9']+", s.lower())

def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa or not sb: return 0.0
    return len(sa & sb) / len(sa | sb)

def exact_phrase_score(query, text):
    q = query.strip().lower()
    t = text.lower()
    if not q: return 0.0
    if q in t: return 1.0
    return 0.0

def mode_topic_boost(topic):
    topic_norm = str(topic).strip()
    if MODE in MODE_TOPIC_MAP and topic_norm in MODE_TOPIC_MAP[MODE]:
        return 0.25
    return 0.0

def rank_entries(user_input, top_k=TOP_K_CONTEXT):
    qtoks = tokenize(user_input)
    scored = []
    for e in KB:
        ttoks = tokenize(e["text"])
        score = 0.0
        score += 1.5 * exact_phrase_score(user_input, e["text"])
        score += 1.0 * jaccard(qtoks, ttoks)
        score += mode_topic_boost(e["topic"])
        # slight preference to similar level keywords
        if any(k in user_input.lower() for k in ["beginner","new","first","v0","v1"]):
            if e["level"].lower().startswith("beginner"): score += 0.1
        if any(k in user_input.lower() for k in ["advanced","power","campus","v7","v8","proj"]):
            if e["level"].lower().startswith("advanced"): score += 0.1
        scored.append((score, e))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:top_k] if _ > 0.0] or [e for _, e in scored[:top_k]]

def build_context_block(entries):
    out = []
    for i, e in enumerate(entries, 1):
        out.append(f"[{i}] Topic: {e['topic']}  Level: {e['level']}\n{e['text']}")
    return "\n\n".join(out)

def clean_deepseek_output(text):
    if not text: return ""
    # Remove XML-like think tags
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S|re.I)
    # Remove "Thinking... ...done thinking." style dumps
    text = re.sub(r"Thinking\.\.\..*?\.{3}done thinking\.", "", text, flags=re.S|re.I)
    # Remove stray “Thought:” lines often prefixed
    text = re.sub(r"(?im)^\s*thoughts?:.*?$", "", text)
    return text.strip()

def climber_wall_loading():
    climber, wall_block, height = "🧗", "⬜", 8
    for step in range(height):
        wall = [wall_block] * height
        wall[height - 1 - step] = climber
        sys.stdout.write("\r" + "\n".join(wall))
        sys.stdout.flush()
        time.sleep(0.18)
        if step != height - 1:
            sys.stdout.write("\033[F" * height)
    sys.stdout.write("\r" + "\n" * height)

# -------------------------- Profiles --------------------------
def profile_path(username):
    safe = re.sub(r"[^a-z0-9_\-]+", "_", username.lower())
    return PROFILE_DIR / f"profile_{safe}.json"

def load_profile(username):
    p = profile_path(username)
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "username": username,
        "goals": "",
        "preferences": {
            "styles": [],            # e.g., ["overhang","slab"]
            "weaknesses": []         # e.g., ["crimps","heel hooks"]
        },
        "history": [],               # list of {"query":..., "mode":..., "timestamp":...}
        "topic_counts": {}           # aggregated topic usage
    }

def save_profile(profile):
    with open(profile_path(profile["username"]), "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

def update_profile_after_query(profile, user_input, entries):
    from time import time as now
    profile["history"].append({"query": user_input, "mode": MODE, "timestamp": int(now())})
    counts = Counter([e["topic"] for e in entries])
    for k, v in counts.items():
        profile["topic_counts"][k] = profile["topic_counts"].get(k, 0) + v

# Optional: very light personalization hints based on profile
def build_personalization_hint(profile):
    hints = []
    if profile.get("goals"):
        hints.append(f"User goal: {profile['goals']}.")
    if profile["preferences"]["styles"]:
        hints.append(f"Preferred style(s): {', '.join(profile['preferences']['styles'])}.")
    if profile["preferences"]["weaknesses"]:
        hints.append(f"Known weaknesses: {', '.join(profile['preferences']['weaknesses'])}.")
    # top topics user asks about
    if profile["topic_counts"]:
        top = sorted(profile["topic_counts"].items(), key=lambda x: x[1], reverse=True)[:3]
        if top:
            hints.append("Frequently discussed topics: " + ", ".join([f"{k}({v})" for k, v in top]) + ".")
    return " ".join(hints)

# -------------------------- Chat Core --------------------------
history = []

def build_prompt(user_input, context_block, personalization_hint):
    return (
        f"{SYSTEM_STYLE}\n\n"
        f"MODE: {MODE.upper()}. Use content relevant to this mode.\n"
        f"PERSONALIZATION: {personalization_hint}\n\n"
        f"TOP RETRIEVED CONTEXT (ranked):\n{context_block}\n\n"
        "INSTRUCTIONS:\n"
        "- Answer the user's last message.\n"
        "- Be concise; prefer bullets or short paragraphs.\n"
        "- If safety risks exist, include a brief safety note.\n"
        "- If you’re unsure, say so briefly and suggest next steps/tests.\n\n"
        f"Conversation:\n" + "\n".join(history[-8:]) + f"\nUser: {user_input}\nAssistant:"
    )

def ollama_run(prompt):
    loader = threading.Thread(target=climber_wall_loading, daemon=True)
    loader.start()
    proc = subprocess.Popen(
        ["ollama", "run", MODEL_NAME],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore"  # prevents UnicodeDecodeError on Windows consoles
    )
    stdout, stderr = proc.communicate(prompt)
    # stop loader
    loader.join(0)
    if stderr:
        print("\nDEBUG stderr:", stderr)
    return clean_deepseek_output(stdout)

def chat_once(profile, user_input):
    # Commands
    global MODE
    if user_input.strip().lower().startswith("/mode"):
        parts = user_input.split()
        if len(parts) >= 2 and parts[1].lower() in MODE_TOPIC_MAP:
            MODE = parts[1].lower()
            return f"Mode set to **{MODE}**."
        return f"Usage: /mode coach | safety | competition"
    if user_input.strip().lower().startswith("/set goal"):
        goal = user_input.partition("/set goal")[2].strip(": ").strip()
        profile["goals"] = goal
        save_profile(profile)
        return f"Saved goal: {goal}"
    if user_input.strip().lower().startswith("/add style"):
        style = user_input.partition("/add style")[2].strip(": ").strip()
        if style and style not in profile["preferences"]["styles"]:
            profile["preferences"]["styles"].append(style)
            save_profile(profile)
        return f"Added style: {style or '(none)'}"
    if user_input.strip().lower().startswith("/add weakness"):
        wk = user_input.partition("/add weakness")[2].strip(": ").strip()
        if wk and wk not in profile["preferences"]["weaknesses"]:
            profile["preferences"]["weaknesses"].append(wk)
            save_profile(profile)
        return f"Added weakness: {wk or '(none)'}"
    if user_input.strip().lower() == "/profile":
        return json.dumps(profile, indent=2)
    if user_input.strip().lower() == "/help":
        return (
            "Commands:\n"
            "/mode coach|safety|competition\n"
            "/set goal: <text>\n"
            "/add style: <style>\n"
            "/add weakness: <thing>\n"
            "/profile\n"
            "/help\n"
            "/quit"
        )

    # Retrieval
    entries = rank_entries(user_input, TOP_K_CONTEXT)
    context_block = build_context_block(entries)
    personalization_hint = build_personalization_hint(profile)
    prompt = build_prompt(user_input, context_block, personalization_hint)

    # Model
    reply = ollama_run(prompt) or "Error: no response from the model."
    # Update transcript and profile
    history.append(f"User: {user_input}")
    history.append(f"Assistant: {reply}")
    update_profile_after_query(profile, user_input, entries)
    save_profile(profile)
    return reply

# -------------------------- Main Loop --------------------------
def main():
    print("Bouldering Coach Bot (Smart) ready! Type '/help' for commands. Type '/quit' to exit.")
    username = input("Enter your name (for a local profile): ").strip() or "guest"
    profile = load_profile(username)
    print(f"Hello, {profile['username']}! Current mode: {MODE}.")
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "/quit"}:
            print("Bye!")
            break
        reply = chat_once(profile, user_input)
        print("Bot:", reply, flush=True)

if __name__ == "__main__":
    main()

