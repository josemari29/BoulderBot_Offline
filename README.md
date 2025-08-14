# BoulderBot_Offline
BoulderBot_Offline – AI-Powered Bouldering Coach (Offline Version)

BoulderBot_Offline is a locally runnable AI chatbot designed to provide personalized bouldering advice, tips, and safety guidance without requiring an internet connection. Built using the DeepSeek-R1:8B model, this offline version integrates a custom knowledge base of climbing techniques and training strategies, making it an ideal companion for climbers of all skill levels.

Key Features:

Offline NLP Chatbot: Fully functional AI assistant capable of answering bouldering-related questions without an internet connection.

Custom Knowledge Base: Uses a JSON dataset of curated bouldering questions and answers to provide context-aware guidance.

Concise, Friendly Responses: Model output is filtered to remove internal “thinking” content, delivering clean, actionable advice.

Interactive CLI Experience: Includes a vertical “climber wall” loading animation for a fun, immersive interface while the model generates responses.

Conversation History Tracking: Maintains dialogue context for more relevant follow-up advice.

Extensible Dataset: Users can easily expand the knowledge base with additional climbing tips or training insights.

Use Cases:

Quickly get climbing advice while at the gym or outdoors without needing a Wi-Fi connection.

Train beginner or intermediate climbers on grip, technique, route-finding, and safety practices.

Serve as a prototype for offline AI assistants in niche applications.

Tech Stack:

Python 3.10+

DeepSeek-R1:8B offline model via Ollama

JSON for knowledge base storage

Threading and subprocess modules for interactive CLI experience

Getting Started:
Clone the repository or download the files, ensure the DeepSeek-R1:8B model is installed locally via Ollama, and run BoulderBot_Offline.py. Type your climbing questions into the CLI and receive context-aware advice in real time.
