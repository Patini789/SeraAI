"""Load and validate environment variables."""
# settings.py
import os
import json
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(__file__).resolve().parent.parent / "env" / ".env"
load_dotenv(dotenv_path)

class Settings:
    def __init__(self):
        from pathlib import Path

        base = Path(__file__).resolve().parent.parent
        self.enable_discord_bot = os.getenv("ENABLE_DISCORD_BOT", "true").lower() == "true"
        self.discord_token = os.getenv("TOKEN")
        self.memory_path = base / "packages" / "memory" / "memories.json"
        self.file_path = base / ".." / "data" / "current_conversation.json"

        self.instructions = os.getenv("INSTRUCTIONS")

        self.model = os.getenv("MODEL")
        self.max_tokens = os.getenv("MAX_TOKENS")
        self.current_model = os.getenv("CURRENT_MODEL")

        self.prompter_route = base / "packages" / "models"

        notify_json = base / "env" / "notify.json"
        if notify_json.exists():
            with open(notify_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.notify_user_ids = list(data.get("usuarios", {}).get("active", {}).values())
                self.notify_channel_ids = list(data.get("canales", {}).get("active", {}).values())

        get_api_path = base / "env" / "personal.json"
        with open(get_api_path, "r") as f:
            self.get_api = json.load(f)

settings = Settings()
