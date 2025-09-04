# 🎙️ AI Realtime Voice & Chat Assistant  

This project is an **AI-powered realtime voice and chat assistant** built with **LiveKit**, **Google Realtime Gemini API**, and **Mem0 for memory persistence**.  
It supports **voice-based interaction**, **noise cancellation**, and can perform tasks such as fetching weather, searching the web, and sending emails.  

---

## 🚀 Features  

- **Realtime AI Assistant** powered by Google Gemini (`gemini-2.0-flash-live-001`).  
- **Voice support** with noise cancellation (using `livekit.plugins.noise_cancellation`).  
- **Contextual memory** persistence with **Mem0**.  
- **Custom Tools Integration**:  
  - 🌦️ `get_weather` → Fetch weather updates.  
  - 🔍 `search_web` → Perform live web searches.  
  - 📧 `send_email` → Send emails directly via assistant.  
- **Session memory handling** (stores previous conversations with users).  

---

## 🛠️ Tech Stack  

- [LiveKit Agents](https://github.com/livekit/agents) – Realtime AI sessions.  
- [Google Realtime Gemini API](https://ai.google.dev/) – LLM backbone.  
- [Mem0](https://mem0.ai) – Memory persistence.  
- [Python `dotenv`](https://pypi.org/project/python-dotenv/) – Environment variables.  

---

## 📂 Project Structure  

```bash
.
├── agent.py              
├── prompts.py           
├── tools.py             
├── .env.local           
└── requirements.txt     
