import sys
import importlib.util
from copyreg import constructor

from config.settings import settings
from Python.io.reader import Reader
from Python.io.APIClient import APIClient
from packages.memory.memory_manager import MemoryManager
from Python.packages.models import model_administrator
from Python.packages.models.model_administrator import ModelAdministrator
from Python.packages.discord_bot.discord_bot import DiscordBot


class App:
    def __init__(self):

        # Initialize model configuration
        self.max_tokens = settings.max_tokens
        model_config = settings.get_api["model"]
        self.api = model_config["api"]
        self.model = model_config["model"]
        self.url = model_config["url"]

        # URL's & model's configuration
        self.api_client = APIClient(
            embedding_url=settings.embedding_url,
            embedding_model=settings.embedding_model,
            completion_url=settings.completion_url,
            completion_model=settings.completion_model
        )
        # Initialize memory manager
        self.memory = MemoryManager(json_path=settings.memory_path, api_client=self.api_client)

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
            "user_ids": settings.user_ids,
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

    def handle_new_message(self, author: str, item: str) -> str:
        """Handle a new user message and return the model response."""

        # Step 1: Format user message
        user_msg = self.constructor_module.user(f"{author}: " + f"{item}")
        self.conversation_history.append(user_msg)

        # Step 2: Retrieve relevant memories
        author_tag = author
        user_memories = self.memory.retrieve(user_msg, top_k=3, min_similarity=0.70, tags=[author_tag])

        global_memories = self.memory.retrieve(item, top_k=2, min_similarity=0.70, tags=["global"])

        sera_memories = self.memory.retrieve(item, top_k=3, min_similarity=0.70, tags=["Sera"])

        combined_memories = list(dict.fromkeys(user_memories + global_memories + sera_memories))


        print(f"Relevant memories ({len(combined_memories)}):")
        for rec in combined_memories:
            print(rec)

        if combined_memories:
            formatted_memory = self.constructor_module.memory(combined_memories)
        else:
            formatted_memory = ""
            print("No memories.")

        # Step 3: Construct prompt
        completion_marker = self.constructor_module.bot_completion()
        full_prompt = (
                self.instructions +
                "\n" + formatted_memory +
                "\n" + "\n".join(self.conversation_history) +
                completion_marker
        )

        # ✅ DEBUG: Mostrar prompt final que verá la IA
        print("📝 PROMPT Send:\n" + "-" * 50)
        print(full_prompt)
        print("-" * 50)

        # Step 4: Get completion
        response = self.api_client.complete(
            full_prompt,
            max_tokens=self.max_tokens,
            temperature=0.3,
            top_p=0.4
        )

        # Step 5: Append and return
        bot_response = completion_marker + response + self.constructor_module.bot_end() + "\n"
        self.conversation_history.append(bot_response)

        return response

    def run(self):
        """Start all registered services."""
        for service in self.services:
            service.start()
