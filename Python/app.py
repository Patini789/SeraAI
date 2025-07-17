#import sys
#import importlib.util
#from copyreg import constructor

import threading
import asyncio
import json
import re

from config.settings import settings
from Python.io.reader import Reader
from Python.io.APIClient import APIClient
from packages.memory.memory_manager import MemoryManager
from Python.packages.models.model_administrator import ModelAdministrator
from Python.packages.discord_bot.discord_bot import DiscordBot
from Python.packages.tts import TTS

class App:
    def __init__(self):

        # Initialize model configuration
        self.max_tokens = settings.max_tokens
        model_config = settings.get_api["model"]
        self.api = model_config["api"]
        self.model = model_config["model"]
        self.url = model_config["url"]

        # Configure URLs and model settings
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
            self.prompter_path = settings.prompter_route / f"{self.api}.py"
            admin = ModelAdministrator()
            self.constructor_module = admin.load_module_from_path(self.prompter_path)
        except Exception as e:
            print(f"❌ Error loading model from {getattr(self, 'prompter_path', 'unknown path')}: {e}")
            self.constructor_module = None

        print(f"Loaded prompt constructor from: {self.prompter_path}")

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

        # Text-to-Speech service
        if settings.voice_active:
            self.tts = TTS(settings.rate, settings.pitch, settings.voice)
            self.services.append(self.tts)

        # Reader service
        self.reader = Reader(
            file_path=settings.file_path,
            on_new_message_fn=self.handle_new_message
        )
        self.services.append(self.reader)

        # Discord bot service
        if settings.enable_discord_bot:
            print("✅ Discord bot enabled in settings")
            self.services.append(DiscordBot(self.shared_state, on_new_message_fn=self.handle_new_message))

        # Initialize conversation prompt
        self.instructions = self.constructor_module.system(settings.instructions)
        self.conversation_history = [self.instructions]
        self.raw_conversation_log = []

    def handle_new_message(self, author: str, message: str) -> str:
        """Handle a new user message and return the model's response."""

        # Step 1: Format user message
        user_msg = self.constructor_module.user(f"{author}: {message}")
        # Save raw author message
        self.raw_conversation_log.append(f"author: {author}\ncontent: {message}")

        self.conversation_history.append(user_msg)

        # Step 2: Retrieve relevant memories
        author_tag = author
        user_memories = self.memory.retrieve(user_msg, top_k=3, min_similarity=0.70, tags=[author_tag])

        global_memories = self.memory.retrieve(message, top_k=2, min_similarity=0.70, tags=["global"])

        sera_memories = self.memory.retrieve(message, top_k=3, min_similarity=0.70, tags=["Sera"])

        combined_memories = list(dict.fromkeys(user_memories + global_memories + sera_memories))

        print(f"Relevant memories ({len(combined_memories)}):")
        for memory_item in combined_memories:
            print(memory_item)

        if combined_memories:
            formatted_memory = self.constructor_module.memory(combined_memories)
        else:
            formatted_memory = ""
            print("No memories found.")

        # Step 3: Construct prompt
        completion_marker = self.constructor_module.bot_completion()
        full_prompt = (
            self.instructions +
            "\n" + formatted_memory +
            "\n" + "\n".join(self.conversation_history) +
            completion_marker
        )

        # Debug: Show final prompt sent to AI
        print("🏷️ PROMPT Sent:\n" + "-" * 50)
        print(full_prompt)
        print("-" * 50)

        # Step 4: Get completion from API
        response = self.api_client.complete(
            full_prompt,
            max_tokens=self.max_tokens,
            temperature=0.3,
            top_p=0.4
        )

        # Step 5: Append response and return
        # Save raw response
        self.raw_conversation_log.append(f"author: Sera\ncontent: {response}\n")

        bot_response = completion_marker + response + self.constructor_module.bot_end() + "\n"
        self.conversation_history.append(bot_response)

        # Play TTS asynchronously if enabled
        if hasattr(self, 'tts') and self.tts:
            def run_tts():
                try:
                    asyncio.run(self.tts.speak(response))
                except RuntimeError as e:
                    print(f"⚠️ TTS thread error: {e}")

            threading.Thread(target=run_tts, daemon=True).start()

        print("🪧 Response:\n" + "-" * 50)
        print(response)
        print("-" * 50)

        print("🪧 Conversation passed to memory summarizer:\n" + "-" * 50)
        print(self.raw_conversation_log)
        print("-" * 50)

        # Run summarizer in a separate thread to avoid blocking
        threading.Thread(
            target=self._summarize_and_store,
            args=("\n".join(self.raw_conversation_log),),
            daemon=True
        ).start()

        return response

    def _summarize_and_store(self, text: str):
        try:
            summary_prompt = self.constructor_module.memory_summarizer_prompt(text)
            raw_response = self.api_client.complete(summary_prompt, temperature=0.3, max_tokens=256)

            print("🎙️ Raw summary response:")
            print(raw_response)

            # Clean the response: remove ```json or ``` code blocks
            cleaned = re.sub(r"```json\s*|```", "", raw_response).strip()

            if not cleaned:
                print("⚠️ AI returned empty summary.")
                return

            summary_data = json.loads(cleaned)

            if not summary_data.get("recuerdo", False):
                print("Nothing worthy of memory according to AI.")
                return

            summary_text = summary_data["text"]
            tags = summary_data.get("tags", [])

            # Check for similar existing memories
            similar_memories = self.memory.retrieve(
                summary_text, top_k=3, min_similarity=0.87, tags=tags
            )

            if similar_memories:
                print("⛔ Similar memory already exists. Skipping save.")
                return

            self.memory.add_memory(summary_text, tags=tags)
            print("💾 Memory saved successfully.")

        except json.JSONDecodeError as e:
            print(f"⚠️ Memory summary JSON decode error: {e}")
            print("🔍 Received content:")
            print(raw_response)

        except Exception as e:
            print(f"Unexpected error in memory summarization: {e}")

    def run(self):
        """Start all registered services."""
        for service in self.services:
            service.start()
