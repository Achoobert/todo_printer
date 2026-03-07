import discord
import os
import asyncio
import logging
from flask import Flask, request, jsonify
from threading import Thread, Event # Import Event from threading

from .message_router import bot_processor, bot_direct, bot_direct_daily_briefing

logger = logging.getLogger(__name__)

# It's better to load the token from environment variables for security
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot_app = Flask(__name__) # Flask app for the Discord service

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

@bot_app.route("/trigger_thread", methods=["POST"])
def trigger_thread():
    if request.is_json:
        data = request.get_json()
        thread_name = data.get("thread_name")
        if thread_name:
            logger.info(f"Received trigger for thread: {thread_name}")
            # Run the async function in a new task
            if discord_loop: # Ensure the loop is available
                if (thread_name == "goals"):
                    asyncio.run_coroutine_threadsafe(
                        process_latest_thread_message(thread_name, bot_direct_daily_briefing), discord_loop
                    )
                else: # Catch-all for other threads
                    asyncio.run_coroutine_threadsafe(
                        process_latest_thread_message(thread_name, bot_direct), discord_loop
                    )
            else:
                logger.error("Discord event loop not available.")
                return jsonify({"error": "Discord event loop not initialized"}), 500
            # respond to message
            return jsonify({"status": "triggered", "thread_name": thread_name}), 200
        return jsonify({"error": "'thread_name' field missing"}), 400
    # TODO allow input like  "curl -X POST http://localhost:8555/trigger_thread/?thread=progress"
    return jsonify({"error": "Request must be JSON"}), 400

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

def run_flask_app():
    # Wait for the Discord bot to be ready before starting Flask
    logger.info("Flask app waiting for Discord bot to be ready...")
    bot_ready_event.wait() # Block until the bot is ready
    logger.info("Discord bot is ready. Starting Flask app.")
    bot_app.run(host="0.0.0.0", port=8555)

def start_bot():
    # Start Flask app in a separate thread
    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()
    # Start Discord bot in the main thread (blocking call)
    run_discord_bot()
