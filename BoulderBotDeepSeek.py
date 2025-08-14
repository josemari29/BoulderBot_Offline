import subprocess, threading, time, sys, json, re

# Load local bouldering knowledge base
kb = json.load(open("bouldering_dataset.json"))
history = []

def get_context(user_input):
    return "\n".join(
        f"Q: {e['question']}\nA: {e['answer']}"
        for e in kb if user_input.lower() in e["question"].lower()
    )

def climber_wall_loading():
    climber, wall_block, height = "🧗", "⬜", 8
    for step in range(height):
        wall = [wall_block] * height
        wall[height - 1 - step] = climber
        sys.stdout.write("\r" + "\n".join(wall))
        sys.stdout.flush()
        time.sleep(0.3)
        if step != height - 1:
            sys.stdout.write("\033[F" * height)
    sys.stdout.write("\r" + "\n" * height)

def clean_deepseek_output(text):
    # Remove everything between "Thinking..." and "...done thinking."
    cleaned = re.sub(r"Thinking\.\.\..*?\.{3}done thinking\.", "", text, flags=re.S)
    return cleaned.strip()

def chat_bot(user_input):
    history.append(f"User: {user_input}")
    prompt = (
        "You are a friendly and knowledgeable bouldering coach.\n"
        "Answer clearly with tips and keep it simple.\n\n"
        "Do not ramble. Keep it simple to 1-2 paragraphs.\n\n"
        f"{get_context(user_input)}\nConversation history:\n"
        + "\n".join(history) + f"\nUser: {user_input}\nBot:"
    )

    loader = threading.Thread(target=climber_wall_loading)
    loader.start()
    proc = subprocess.Popen(
        ["ollama", "run", "deepseek-r1:8b"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8"
    )
    stdout, stderr = proc.communicate(prompt)
    loader.join(0)

    if stderr:
        print("DEBUG stderr:", stderr)
    reply = clean_deepseek_output(stdout) if stdout else "Error: no response from the model."
    history.append(f"Bot: {reply}")
    return reply

print("Bouldering Coach Bot is ready! Type 'quit' to exit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    print("Bot:", chat_bot(user_input))
