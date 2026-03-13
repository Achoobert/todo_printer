import discord
import os
import sys
import asyncio
import logging
from threading import Event

from .message_router import bot_processor, bot_direct, bot_direct_daily_briefing

logger = logging.getLogger(__name__)

# It's better to load the token from environment variables for security
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")
if not DISCORD_API_TOKEN or not str(DISCORD_API_TOKEN).strip():
    logger.error("DISCORD_API_TOKEN is not set. Set it in the environment (e.g. source .env) before starting.")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Global variable to store the Discord client's event loop
discord_loop = None
# Event to signal that the Discord bot is ready and its loop is available
bot_ready_event = Event() # Use threading.Event

@client.event
async def on_ready():
    global discord_loop
    discord_loop = client.loop
    bot_ready_event.set() # Signal that the bot is ready
    logger.info(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await bot_processor(message, client)

def schedule_trigger_thread(thread_name: str, timeout: float = 30.0) -> bool:
    """Schedule thread processing on the Discord event loop. Returns True if scheduled, False if bot not ready in time."""
    if not thread_name:
        return False
    if not bot_ready_event.wait(timeout=timeout):
        logger.error("Discord bot not ready in time for trigger_thread.")
        return False
    logger.info(f"Scheduling trigger for thread: {thread_name}")
    if thread_name == "goals":
        asyncio.run_coroutine_threadsafe(
            process_latest_thread_message(thread_name, bot_direct_daily_briefing), discord_loop
        )
    else:
        asyncio.run_coroutine_threadsafe(
            process_latest_thread_message(thread_name, bot_direct), discord_loop
        )
    return True


async def process_latest_thread_message(thread_name: str, callback):
    """Fetches the latest message from a specified thread and processes it."""
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == thread_name and isinstance(channel, discord.TextChannel):
                try:
                    # Fetch the latest message
                    latest_message = None
                    async for message in channel.history(limit=1):
                        latest_message = message
                    
                    if latest_message:
                        logger.info(f"Processing latest message from '{thread_name}': {latest_message.content}")
                        if (thread_name == "goals"):
                            await bot_direct(latest_message, client)
                        else:
                            await bot_direct(latest_message, client)
                        # Optionally react to the message to indicate it was processed
                        await latest_message.add_reaction('✅')
                    else:
                        logger.info(f"No messages found in thread '{thread_name}'.")
                except Exception as e:
                    logger.error(f"Error processing thread '{thread_name}': {e}")
                return
    logger.warning(f"Thread '{thread_name}' not found.")

def run_discord_bot():
    client.run(DISCORD_API_TOKEN)

def read_thread_last_message(thread_name):
    return process_latest_thread_message(thread_name, None)


def start_bot():
    run_discord_bot()
