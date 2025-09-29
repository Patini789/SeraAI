# Sera

Sera is a modular conversational system with long-term memory powered by embeddings.
It's still a work in progress, but feel free to try it out if you're curious.

I'm a student, so the project is constantly evolving. In the future, I want Sera to be fully integrated with a UI in Godot (kind of like NeuroSama), support multiple AIs (local or remote), speak using TTS, and generate its own embeddings automatically.

Sera is not an AI by itself — it's a system that connects to AI models and handles conversation flow, memory, and more.

## Features
Full Voice Interaction: Utilizes Whisper for real-time speech-to-text and Edge-TTS for voice responses.

Long-Term Memory: Remembers key details from past conversations using vector embeddings. Memories can be added manually or generated automatically by enabling the CREATE_MEMORIES option.

Highly Configurable: Fine-tune Sera's behavior, activate/deactivate features, and manage settings through the central bot_config.py file.

Schedule Awareness (Beta): Can be loaded with a daily schedule to provide context about ongoing or upcoming events.

## Requirements
This project requires a local server that provides an OpenAI-compatible API. This is essential for Sera to connect to a language model and function correctly.

A popular and easy-to-use option is LM Studio.

## Setup
1. Clone the repository.

2. Install Dpendencies ```pip install -r requirements.txt```

3. Go to the env/ folder and rename the files, removing user. and .txt if present. Then fill in the fields using the examples:

    user..env.txt -> .env
   
    user.modelAPI.json -> modelAPI.json
   
    user.notify.json -> notify.json

    etc.,

   Do the same in the memory/ folder:
  
    user.memories.json -> memories.json

 5. Make sure you have a local server running that supports both embeddings and completion models.

 6. Play with the values in bot_config.py, and active all you want.

 7. Run Sera ```pyton Python```
  
## Ready to Go
Feel free to use or tweak the project however you like — just credit it appropriately.
More features are coming soon!
