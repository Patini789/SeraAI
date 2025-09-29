#app.py

#import sys
#import importlib.util
#from copyreg import constructor
import time
from datetime import datetime
import threading
import asyncio
import json
import re

from .packages.schedules import SchedulesManager
from .config.settings import settings
from .io.reader import Reader
from .io.APIClient import APIClient
from .packages.memory.memory_manager import MemoryManager
from .packages.models.model_administrator import ModelAdministrator
from .packages.discord_bot.discord_bot import DiscordBot
from .packages.tts import TTS
from .io.voice import Voice


class App:
    def __init__(self):
        """Initialize the application with settings and services."""
        # Not optional settings
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

        # Optional settings
        self.voice_active = settings.voice_active
        self.enable_discord_bot = settings.enable_discord_bot
        self.school = settings.school
        self.speech_to_text = settings.speech_to_text
        self.extra_data = settings.extra_data
        #self.image_vision = settings.image_vision temp disable
        self.create_memories = settings.create_memories
        self.use_memories = settings.use_memories

        # Improve de cuality but add latency (a lot *wink*)
        self.translate_enable = settings.translate_enabled

        # Initialize memory manager
        self.memory = MemoryManager(json_path=settings.memory_path, api_client=self.api_client)

        # Emotions
        self.emotion_path = settings.emotion_path

        # Initialize user_context
        self.user_context_json = settings.user_context

        self.constructor_paths = {}

        # Load prompt constructor module
        try:
            self.prompter_path = settings.prompter_route / f"{self.api}.py"
            admin = ModelAdministrator(self.constructor_paths)
            
            self.constructor_module = admin.load_module_from_path(self.prompter_path)
        except Exception as e:
            print(f"❌ Critique Error loading model from {getattr(self, 'prompter_path', 'unknown path')}: {e}")
            self.constructor_module = None

        print(f"Loaded prompt constructor from: {self.prompter_path}")

        # Prepare shared state for external services (e.g., Discord)
        # always include memory and model settings
        self.shared_state = {
            "memory": self.memory,
            "model": self.model,
            "max_tokens": self.max_tokens,
        }

        # If Discord bot is enabled, add related settings to shared_state
        if settings.enable_discord_bot:
            self.shared_state.update({
                "notify_user_ids": settings.notify_user_ids,
                "notify_channel_ids": settings.notify_channel_ids,
                "user_ids": settings.user_ids,
                "user_context_path": settings.user_context_path,
                "discord_names": settings.discord_names,
                "discord_help": settings.discord_help,
            })

        # Register services (reader, bots, etc.)
        self.services = []

        # Reader service NOT OPTIONAL for now
        self.reader = Reader(
            file_path=settings.file_path,
            on_new_message_fn=self.handle_new_message,
        )
        
        self.services.append(self.reader)

        # Text-to-Speech service
        print("voice_active:", settings.voice_active)

        if settings.voice_active:
            self.tts = TTS(settings.rate, settings.pitch, settings.voice, settings.emotion_path)
            self.services.append(self.tts)

        # Discord bot service
        if settings.enable_discord_bot:
            print("✅ Discord bot enabled in settings")
            self.services.append(DiscordBot(self.shared_state, on_new_message_fn=self.handle_new_message, reset_lists=self.reset_lists))

        # Schedules service
        if settings.school:
            print("✅ School mode enabled in settings")
        self.SchedulesManager = SchedulesManager(settings.schedules_path)
        
        self.stt = None
        if settings.speech_to_text:
            self.stt = Voice(
                model_size="large-v3",
                language="es",
                file_path=settings.file_path,
            )
            self.services.append(self.stt)

        # Initialize conversation prompt NOT OPTIONAL
        self.instructions = settings.instructions
        self.current_authors = []
        self.conversation_history = []
        self.raw_conversation_log = []
        self.temporary_memories = []
        self.user_context = []
        self.memory_lifetime = 4

    def reset_lists(self):
        self.instructions = settings.instructions
        self.current_authors = []
        self.conversation_history = []
        self.raw_conversation_log = []
        self.temporary_memories = []
        self.user_context = []
        self.memory_lifetime = 4


    def handle_new_message(self, author: str, message: str) -> str:
        """Handle a new user message and return the model's response."""
        if message == "cls": # TODO boring make it cleaner
            self.reset_lists()
            return "Clean memory and context."
        if self.translate_enable:
            message = self.constructor_module.translator_to_english(message)
            message = self.api_client.complete(
            message,
            max_tokens=self.max_tokens,
            temperature=0.9,
            top_p=0.4
            )
            message = self.constructor_module.clean_answer(message)
            print("Translated message to english:", message)

        # Step 1: Format user message
        user_msg = self.constructor_module.user(f"{author}: {message}") # not optional
        # Save raw author message
        self.raw_conversation_log.append(f"author: {author}\ncontent: {message}") # not optional

        self.conversation_history.append(user_msg) # not optional

        # Step 2: Optional calls to memory retrieval 
        self.optional_system_text = self.pre_handle_options(author, message) # check if's add latency maybe I can optimize it but i think its ok for now python can handle it yupi

        # Add user context if available
        # always active, why not?
        if author in self.user_context_json:
            if author not in self.current_authors:
                print(f"➕ Añadiendo contexto para {author}")
                self.current_authors.append(author)
        combined_user_contexts = []

        for a in self.current_authors:
            ctx = self.user_context_json.get(a, "").strip()
            if ctx:  # Evita contextos vacíos
                combined_user_contexts.append(f"Context of {a}: {ctx}")

        # Get current emotion to show to AI 
        # Not optional if emotion is used
        try:
            with open(self.emotion_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                emotion = data.get("emotion", "")
        except Exception as e:
            print(f"[Emotion Read Error] {e}")
            emotion = ""
        emotion_tag = f"current emotion: {emotion}" if emotion else ""

        # Step 3: Construct prompt

        # Divide de logic of the prompt in systam and message, the system will have the instructions and make the message format
        # This way we can change the system without changing the message format
        # Also we can have different systems for different models also for models with tools can be different, should make two logics?
        date_hour = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dia_es = self.SchedulesManager.get_today_day_name()

        system_prompt_text = (
        f"Day and hour: {date_hour}. "
        #f"Today is: {dia_es}. "
        f"{self.instructions} {emotion_tag}\n"
        f"{self.optional_system_text}\n"
        + "\n".join(combined_user_contexts)
        )

        full_prompt = (
            self.constructor_module.system(system_prompt_text) + # todo change the system logic to constructor_module and paths
            "\n" + "\n".join(self.conversation_history) +
            self.constructor_module.bot_completion()
        )

        # Debug: Show final prompt sent to AI
        print("🏷️ PROMPT Sent:\n" + "-" * 50)
        print(full_prompt)
        print("-" * 50)

        # Step 4: Get completion from API
        response = self.api_client.complete(
            full_prompt,
            max_tokens=self.max_tokens,
            temperature=0.9,
            top_p=0.4
        )
        response = self.constructor_module.clean_answer(response)
        

        response = self.get_emotions(response)

        # Step 5: Append response and return
        # Save raw response
        self.raw_conversation_log.append(f"author: Sera\ncontent: {response}\n")

        bot_response = self.constructor_module.bot_completion() + response + self.constructor_module.bot_end() + "\n"
        self.conversation_history.append(bot_response)


        print("🪧 Response:\n" + "-" * 50)
        print(response)
        print("-" * 50)
        if self.translate_enable:
                response = self.constructor_module.translator_to_spanish(response)
                response= self.api_client.complete(
                response,
                max_tokens=self.max_tokens,
                temperature=0.9,
                top_p=0.4
                )
                response = self.constructor_module.clean_answer(response)
                print("Translated message to spanish:", response)

        # finally handle options
        self.post_handle_options(response)

        return response
    
    def pre_handle_options(self, author: str, message: str):
        """Handle special commands before processing the message."""
        """System prompt logic, if go after is because is from system and is not a tool from the model."""
        # 1/2 Memories (optional) 

        # Todo optimice this, avoid duplicate calls, its the same embedding
        if self.use_memories:
            author_tag = author
            user_memories = self.memory.retrieve(message, top_k=3, min_similarity=0.80, tags=[author_tag]) 
            global_memories = self.memory.retrieve(message, top_k=2, min_similarity=0.70, tags=["global"])
            sera_memories = self.memory.retrieve(message, top_k=3, min_similarity=0.80, tags=["Sera"])

            # Retrieve extra memories if enabled
        if settings.extra_data:
            extra_context_lines = []
            for term in settings.extra_data:
                # Check if extra_data has context for the AI
                print("term: ", term)
                extra_data_context = self.user_context_json.get(term, "")
                if extra_data_context:
                    extra_context_lines.append(f"🔑 Context for '{term}': {extra_data_context}")
                else:
                    #extra_context_lines.append(f"🔑 Context for '{term}': (no information)")
                    pass

                extra_memories = self.memory.retrieve(message, top_k=2, min_similarity=0.70, tags=[term])
                for mem in extra_memories:
                    if mem not in [m["memory"] for m in self.temporary_memories]:
                        extended_lifetime = max(self.memory_lifetime - 1, 2)
                        self.temporary_memories.append({
                            "memory": mem,
                            "turns_left": extended_lifetime
                        })
            print(f"📚 Loaded extra_data memories for terms: {settings.extra_data}")
        else:
            extra_context_lines = []

        try:
            new_memories = user_memories + global_memories + sera_memories
        except UnboundLocalError:
            new_memories = []
        for mem in new_memories:
            if mem not in [m["memory"] for m in self.temporary_memories]:
                self.temporary_memories.append({"memory": mem, "turns_left": self.memory_lifetime})

        self.temporary_memories = [
            {"memory": m["memory"], "turns_left": m["turns_left"] - 1}
            for m in self.temporary_memories if m["turns_left"] > 1
        ]
        self.temporary_memories = [
            m for m in self.temporary_memories if m["turns_left"] > 0
        ]

        combined_memories = self.memory.deduplicate_memories([m["memory"] for m in self.temporary_memories])

        print(f"🧠 Relevant memories with lifetime ({len(self.temporary_memories)}):")
        for m in self.temporary_memories:
            print(f"({m['turns_left']} turns left) [{m['memory']['days_ago']} days_ago] {m['memory']['text']}")

        memory_lines = []
        # Add memories if any
        if combined_memories:
            for mem in combined_memories:
                memory_lines.append(f"[{mem['days_ago']} days_ago] {mem['text']}")
        else:
            print("No memories found.")

        # Memorias relevantes
        memory_lines = [f"[{mem['days_ago']} days_ago] {mem['text']}" for mem in combined_memories]

        # Construcción del texto final con extra_data al inicio
        system_text = "\n".join(extra_context_lines + memory_lines) if (extra_context_lines or memory_lines) else ""


        # 2/2 School schedule (optional) --not ready just for testing
        if self.school:
            # Spanish testing, will be in a lot more languages later
            date_hour = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # dia_es still works as the function returns the Spanish day name
            today_day_name = self.SchedulesManager.get_today_day_name() 
            tasks = self.SchedulesManager.load_today_schedule()

            tasks_prompt = []
            for t in tasks:
                if isinstance(t, dict):
                    # Use the updated English keys from the dictionary
                    if t.get('RemainingTime') == 'Finished':
                        time_passed = t.get('HoursSinceFinished', 'a while ago')
                        # Also updated the output string to English for consistency
                        tasks_prompt.append(f"Class '{t.get('Materia')}' finished {time_passed} ago.")
                    else:
                        tasks_prompt.append(str(t))
                else:
                    tasks_prompt.append(str(t))
            
            if tasks:
                # Updated the system text to English
                system_text += "\n\nToday's schedule:\n" + "\n".join(tasks_prompt)
            else:
                system_text += "\n\nNo classes today."

        return system_text

    def post_handle_options(self, response: str):
        """Handle special commands after processing the message."""
        # Play TTS asynchronously if enabled
        if self.tts:
            def run_tts():
                try:
                    asyncio.run(self.tts.speak(response, self.stt))
                    
                except RuntimeError as e:
                    print(f"⚠️ TTS thread error: {e}")

            threading.Thread(target=run_tts, daemon=True).start()

        if self.create_memories:
            print("🪧 Conversation passed to memory summarizer:\n" + "-" * 50)
            print(self.raw_conversation_log)
            print("-" * 50)
            
            # Run summarizer in a separate thread to avoid blocking
            threading.Thread(
                target=self._summarize_and_store,
                args=("\n".join(self.raw_conversation_log),),
                daemon=True
            ).start()   

    def _summarize_and_store(self, text: str):
        """save a memory if relevant"""
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
            self.raw_conversation_log.clear()
            print("💾 Memory saved successfully.")

        except json.JSONDecodeError as e:
            print(f"⚠️ Memory summary JSON decode error: {e}")
            print("🔍 Received content:")
            print(raw_response)

        except Exception as e:
            print(f"Unexpected error in memory summarization: {e}")

    def tag_memories(memories, tag_prefix):
        return [{"memory": mem, "tag": tag_prefix} for mem in memories]

    def get_emotions(self, response):
        emociones_validas = {"Feliz", "Triste", "Molesta", "Emocionada", "Sadica"}

        try:
            encontrados = re.findall(r"#(\w+)", response)
            emociones = [e for e in encontrados if e in emociones_validas]

            if emociones:
                # Cargar archivo actual
                with open(self.emotion_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Asegurarse de que "queue" exista
                data.setdefault("queue", [])

                # Agregar emociones sin duplicar
                for e in emociones:
                    if e not in data["queue"]:
                        data["queue"].append(e)

                # Guardar el archivo actualizado
                with open(self.emotion_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

            #response = re.sub(r"#(\w+)", "", response).strip()

        except Exception as e:
            print(f"[Emotion detection error] {e}")

        return response

    def start_non_blocking_services(self):
        """Start non-blocking services."""
        for service in [s for s in self.services if not isinstance(s, DiscordBot)]:
            if service:  # make sure the service is initialized
                service.start()
                
    def run(self):
        """Start all registered services."""
        # Start non-blocking services in a separate thread
        services_thread = threading.Thread(target=self.start_non_blocking_services, daemon=True)
        services_thread.start()

        # Start the Discord bot in the main thread (it's a blocking loop)
        # Make sure DiscordBot is in the list of services, but that its .start()
        # is the last thing to run in the main thread
        if settings.enable_discord_bot:
            discord_service = next((s for s in self.services if isinstance(s, DiscordBot)), None)
            if discord_service:
                discord_service.start()
        else:
            # If Discord is not active, you can keep the main thread in a loop
            # to keep the program alive.
            print("Running in non-discord mode. Press Ctrl+C to exit.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Exiting.")

    #Todo migrate to SQL
    #Todo separate de system's prompot logic in their own module
    #Todo add a config to enable/disable features like tts, discord, stt
    #Todo make a better speech text cleaner
    #Todo manage with a monitor to the handle_new_message to avoid overlapping messages and breaking the port url
    #stream option? the api supports it, i have to check how to manage it with the app

