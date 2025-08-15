import subprocess
import json
import sys

# =============================
# Config
# =============================
DATASET_FILE = "bouldering_dataset.json"  # Must exist in same folder
MODEL_NAME = "deepseek-r1:8b"

# Load local dataset
try:
    kb = json.load(open(DATASET_FILE, encoding="utf-8"))
except FileNotFoundError:
    print(f"ERROR: Could not find {DATASET_FILE}")
    sys.exit(1)

history = []
current_mode = "Coach"  # Default mode

# =============================
# Mode Prompts
# =============================
MODES = {
    "Coach": "You are a friendly and knowledgeable bouldering coach. Give clear, practical advice on climbing techniques, grip, training, and progression.",
    "Safety": "You are a bouldering safety expert. Focus on injury prevention, proper warm-ups, spotting, and fall safety.",
    "Competition": "You are a bouldering competition strategist. Give tips for efficiency, route reading, pacing, and mental focus."
}

# =============================
# Weighted Knowledge Retrieval
# =============================
def get_context(user_input):
    matches = []
    for e in kb:
        question = e["question"].lower()
        if any(word in question for word in user_input.lower().split()):
            score = sum(user_input.lower().count(word) for word in question.split())
            matches.append((score, f"Q: {e['question']}\nA: {e['answer']}"))
    matches.sort(reverse=True, key=lambda x: x[0])
    return "\n".join(m[1] for m in matches[:5])  # Top 5 matches

# =============================
# Bot Interaction
# =============================
def chat_with_bouldering_bot(user_input):
    global current_mode

    # Mode switching command
    if user_input.lower().startswith("/mode"):
        parts = user_input.split(maxsplit=1)
        if len(parts) == 2 and parts[1].capitalize() in MODES:
            current_mode = parts[1].capitalize()
            return f"✅ Mode switched to: {current_mode}"
        else:
            return f"❌ Invalid mode. Available modes: {', '.join(MODES.keys())}"

    # Prepare context
    context = get_context(user_input)
    history.append(f"User: {user_input}")

    # Build prompt
    prompt = f"""{MODES[current_mode]}

Relevant knowledge base:
{context if context else "No matching data found in local KB."}

Conversation history:
{chr(10).join(history)}

User: {user_input}
Bot:"""

    # Debug info
    print("\n=== DEBUG: PROMPT SENT TO MODEL ===")
    print(prompt)
    print("===================================\n")

    # Run Ollama query
    result = subprocess.run(
        ["ollama", "query", MODEL_NAME, "--prompt", prompt],
        capture_output=True,
        text=True
    )

    # Debug: print raw output
    print("DEBUG raw stdout:", result.stdout.strip())
    print("DEBUG raw stderr:", result.stderr.strip())

    reply = result.stdout.strip() if result.stdout else "Error: No response from model."
    history.append(f"Bot: {reply}")
    return reply

# =============================
# Main Loop
# =============================
print("🤖 BoulderBot DeepSeek Debug Mode")
print("Type '/mode Coach', '/mode Safety', or '/mode Competition' to switch modes.")
print("Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    print("Bot:", chat_with_bouldering_bot(user_input))
