"""discord_bot.py — Discord events handler module for the Sera app."""

import asyncio
import json

import discord
from discord.ext import commands
from Python.config.settings import settings
from typing import Callable, Any

# Define intents correctly
intents = discord.Intents.default()
intents.message_content = True


class DiscordBot:
    def __init__(
            self,
            shared_state: dict[str, Any],
            on_new_message_fn: Callable[[str, str], str],
            reset_lists: Callable[[], None] = None  # <-- Aquí lo agregas
    ):
        self.shared_state = shared_state
        self.bot = commands.Bot(command_prefix='$', intents=intents)
        self.on_new_message_fn = on_new_message_fn
        self.reset_lists = reset_lists

        # List of user IDs to notify
        self.ids_to_notify = shared_state.get("notify_user_ids", [])
        self.user_ids = shared_state.get("user_ids", [])

        # List of channel IDs to notify
        self.channels_to_notify = shared_state.get("notify_channel_ids", [])

        self.user_context_path = shared_state.get("user_context_path", None)

        self.discord_names = shared_state.get("discord_names", {})

        self.discord_help = shared_state.get("discord_help", "")

        @self.bot.event
        async def on_ready():
            print(f'✅ Bot connected as {self.bot.user}')
            for user_id in self.ids_to_notify:
                try:
                    user = await self.bot.fetch_user(user_id)
                    if user:
                        await user.send("Sorry, I need your attention.")
                        print(f"✅ Message sent to {user.name} ({user.id})")
                except Exception as e:
                    print(f"Could not send message to {user_id}: {e}")

            for channel_id in self.channels_to_notify:
                try:
                    channel = await self.bot.fetch_channel(channel_id)
                    if channel:
                        await channel.send("Hi there! I'm online again.")
                        print(f"✅ Message sent to {channel.name} ({channel_id})")
                except Exception as e:
                    print(f"Could not send message to channel {channel_id}: {e}")

        async def send_custom_message(self, author, content):
            if author in self.user_ids:
                user_id = self.user_ids[author]
                user = await self.bot.fetch_user(user_id)
                await user.send(content)
            else:
                print(f"Incorrect author {author}")

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            author_name = str(message.author.name)
            if author_name in self.discord_names:
                author = self.discord_names[author_name]
            else:
                print("Nickname not found using default.")
                author = author_name

            if message.content.startswith('$help'):
                answer = self.discord_help
                await message.channel.send(answer)

            if message.content.startswith('$chat '):
                content = message.content[len('$chat '):]

                answer = await asyncio.to_thread(self.on_new_message_fn, author, content)

                if not answer:
                    await message.channel.send("An error occurred.")
                    return

                print(f"Author: {message.author} (ID: {message.author.id})")
                print(f"Channel: {message.channel} (ID: {message.channel.id})")

                # Split and send if the message exceeds Discord's limit
                max_len = 2000
                parts = [answer[i:i + max_len] for i in range(0, len(answer), max_len)]
                for part in parts:
                    await message.channel.send(part)
            if message.content.startswith('$cls'):
                if self.reset_lists:
                    self.reset_lists()
                    await message.channel.send("Cleaning memory")
                else:
                    await message.channel.send("Operation fail")

            if message.content.startswith('$context '):
                try:
                    with open(self.user_context_path, "r") as f:
                        user_context = json.load(f)
                except FileNotFoundError:
                    user_context = {}
                new_context = message.content[len('$context '):].strip()

                user_context[author] = new_context
                with open(self.user_context_path, "w") as f:
                    json.dump(user_context, f, indent=4, ensure_ascii=False)
                print(f"✅ Context upgraded for {author}")
                await message.channel.send(f"Context upgraded for {author}")

            if message.content.startswith('$check '):
                try:
                    author_to_check = message.content[len('$check '):].strip()
                    with open(self.user_context_path, "r") as f:
                        user_context = json.load(f)
                    if author_to_check == "list":
                        for user in user_context:
                            await message.channel.send(f"Context for {user}: {user_context[user]}")
                        return
                    try:
                        await message.channel.send(f"Context for {author_to_check}: {user_context[author_to_check]}")
                    except KeyError:
                        await message.channel.send(f"No author '{author_to_check}' found.")
                except FileNotFoundError:
                    await message.channel.send("Operation fail")

    def start(self):
        self.bot.run(settings.discord_token)
