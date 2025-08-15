---

🧗 **BoulderBot\_Offline**

**AI-Powered Bouldering Coach – Works 100% Offline**

BoulderBot\_Offline is a **fully offline AI chatbot** that gives **personalized bouldering tips, safety guidance, and training advice** — no Wi-Fi required.

Powered by the **DeepSeek-R1:8B** model and a **custom climbing knowledge base**, it’s your on-demand coach whether you’re in the gym, at the crag, or training at home.

---

## 🚀 **Features**

* 📡 **Completely Offline** – Runs locally, no internet or cloud access needed.
* 🧠 **Custom Climbing Knowledge Base** – Covers grip, movement, route reading, and injury prevention.
* 💬 **Clean, Actionable Responses** – Filters out AI “thinking” for clear answers.
* 🎮 **Immersive CLI Experience** – Vertical “climber wall” loading animation while generating replies.
* 🔄 **Context-Aware Conversations** – Maintains dialogue history for better follow-up advice.
* 🛠 **Extensible Dataset** – Easily add new climbing tips or training info.

---

## 🏆 **Use Cases**

* Quick beta & safety tips without a phone signal.
* Beginner coaching on grip, footwork, and efficiency.
* Prototype for niche, offline AI assistants.

---

## 🛠 **Tech Stack**

| Component        | Details                                    |
| ---------------- | ------------------------------------------ |
| **Language**     | Python 3.10+                               |
| **Model**        | DeepSeek-R1:8B via Ollama (offline)        |
| **Data Storage** | JSON                                       |
| **Interface**    | CLI with threading & subprocess animations |

---

## 📦 **Installation & Setup**

**1️⃣ Clone the repository**

```bash
git clone https://github.com/yourusername/BoulderBot_Offline.git
cd BoulderBot_Offline
```

**2️⃣ Install dependencies**

```bash
pip install -r requirements.txt
```

**3️⃣ Install the model via Ollama**

```bash
ollama pull deepseek-r1:8b
```

**4️⃣ Run BoulderBot**

```bash
python BoulderBot_Offline.py
```

**5️⃣ Start chatting!**
Example:

```
> How can I improve my heel hooks?
```

---

## 📄 **License**

MIT License – Free to use, modify, and share.


