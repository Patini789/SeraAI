import sys
import importlib.util
from copyreg import constructor

from config.settings import settings
from Python.io.reader import Reader
from Python.io.writer import Writer
from packages.memory.manager import MemoryManager
from Python.packages.models import model_administrator
from Python.packages.models.model_administrator import ModelAdministrator
from Python.packages.discord_bot.discord_bot import DiscordBot


class App:
    def __init__(self):
        # Initialize memory manager
        self.memory = MemoryManager(json_path=settings.memory_path)

        # Initialize model configuration
        self.max_tokens = settings.max_tokens
        model_config = settings.get_api["model"]
        self.api = model_config["api"]
        self.model = model_config["model"]
        self.url = model_config["url"]

        # Initialize writer
        self.writer = Writer(
            url=self.url,
            model=self.model
        )

        # Load prompt constructor module
        try:
            self.prompter_route = settings.prompter_route / f"{self.api}.py"
            admin = ModelAdministrator()
            self.constructor_module = admin.load_module_from_path(self.prompter_route)
        except Exception as e:
            print(f"❌ Error loading model from {getattr(self, 'prompter_route', 'unknown path')}: {e}")
            self.constructor_module = None

        print(f"Loaded prompt constructor from: {self.prompter_route}")

        # Prepare shared state for external services (e.g., Discord)
        self.shared_state = {
            "memory": self.memory,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "notify_user_ids": settings.notify_user_ids,
            "notify_channel_ids": settings.notify_channel_ids,
        }

        # Register services (reader, bots, etc.)
        self.services = []
        self.reader = Reader(
            file_path=settings.file_path,
            on_new_message_fn=self.handle_new_message
        )
        self.services.append(self.reader)

        if settings.enable_discord_bot:
            print("✅ Discord bot enabled in settings")
            self.services.append(DiscordBot(self.shared_state, on_new_message_fn=self.handle_new_message))

        # Initialize conversation prompt
        self.instructions = self.constructor_module.system(settings.instructions)
        self.conversation_history = [self.instructions]

    def handle_new_message(self, item: str) -> str:
        """Handle a new user message and return the model response."""

        # Format user message
        user_msg = self.constructor_module.user(item)
        self.conversation_history.append(user_msg)

        # Build prompt
        completion_marker = self.constructor_module.bot_completion()
        full_prompt = "\n".join(self.conversation_history) + completion_marker

        # Generate model response
        response = self.writer.send(full_prompt)

        # Add bot response to conversation history
        bot_response = completion_marker + response + self.constructor_module.bot_end() + "\n"
        self.conversation_history.append(bot_response)

        return response

    def run(self):
        """Start all registered services."""
        for service in self.services:
            service.start()
