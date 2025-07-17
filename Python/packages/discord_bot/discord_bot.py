"""discord_bot.py — Discord events handler module for the Sera app."""

import asyncio
import discord
from discord.ext import commands
from Python.config.settings import settings
from typing import Callable, Any

# Define intents correctly
intents = discord.Intents.default()
intents.message_content = True


class DiscordBot:
    def __init__(self, shared_state: dict[str, Any], on_new_message_fn: Callable[[str, str], str]):
        self.shared_state = shared_state
        self.bot = commands.Bot(command_prefix='$', intents=intents)
        self.on_new_message_fn = on_new_message_fn

        # List of user IDs to notify
        self.ids_to_notify = shared_state.get("notify_user_ids", [])
        self.user_ids = shared_state.get("user_ids", [])

        # List of channel IDs to notify
        self.channels_to_notify = shared_state.get("notify_channel_ids", [])

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

            if message.content.startswith('$chat '):
                content = message.content[len('$chat '):]

                answer = await asyncio.to_thread(self.on_new_message_fn, message.author, content)

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

    def start(self):
        self.bot.run(settings.discord_token)
