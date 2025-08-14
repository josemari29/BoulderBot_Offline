import subprocess

def chat_with_bouldering_bot(user_input):
    prompt = f"""
You are a friendly and knowledgeable bouldering coach. Answer clearly and give practical advice about climbing techniques, grip, training, and safety.

User question: {user_input}
Bot:
"""
    # Run Ollama query
    result = subprocess.run(
        ["ollama", "query", "deepseek-r1:8b", "--prompt", prompt],
        capture_output=True,
        text=True
    )
    
    # Debug: print raw output
    print("DEBUG raw stdout:", result.stdout)
    print("DEBUG raw stderr:", result.stderr)
    
    # Return stripped stdout
    return result.stdout.strip()

print("Bouldering Bot (DeepSeek-R1:8B) is ready! Type 'quit' to exit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    reply = chat_with_bouldering_bot(user_input)
    print("Bot:", reply)
