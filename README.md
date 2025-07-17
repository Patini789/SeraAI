# Sera

Sera is a modular conversational system with long-term memory powered by embeddings.
It's still a work in progress, but feel free to try it out if you're curious.

I'm a student, so the project is constantly evolving. In the future, I want Sera to be fully integrated with a UI in Godot (kind of like NeuroSama), support multiple AIs (local or remote), speak using TTS, and generate its own embeddings automatically.

Sera is not an AI by itself — it's a system that connects to AI models and handles conversation flow, memory, and more.

## Setup
1. Clone the repository.

2. Go to the env/ folder and rename the files, removing user. and .txt if present. Then fill in the fields using the examples:

    user.env.txt -> .env
   
    user.modelAPI.json -> modelAPI.json
   
    user.notify.json -> notify.json

4. Do the same in the memory/ folder:
  
    user.memories.json -> memories.json

 5. Make sure you have a local server running that supports both embeddings and completion models.
  
## Ready to Go
Feel free to use or tweak the project however you like — just credit it appropriately.
More features are coming soon!
