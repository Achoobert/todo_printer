import asyncio
import aiohttp
import schedule
import time
import logging

logger = logging.getLogger(__name__)

# Configuration for scheduled tasks
# Example: {"thread_name": "tasks", "schedule_time": "10:00"}
SCHEDULED_TASKS = [
    {"thread_name": "garbage", "schedule_time": "6:30"},
    {"thread_name": "progress", "schedule_time": "6:31"},
]

async def send_discord_message_trigger(thread_name: str):
    """Sends a POST request to the Discord service to trigger message fetching."""
    discord_service_url = "http://localhost:8555/trigger_thread" # Assuming this endpoint will be created in bot.py
    payload = {"thread_name": thread_name}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(discord_service_url, json=payload) as response:
                response.raise_for_status()
                logger.info(f"Successfully triggered Discord service for thread '{thread_name}'.")
    except aiohttp.ClientError as e:
        logger.error(f"Failed to trigger Discord service for thread '{thread_name}': {e}")

def job(thread_name: str):
    """The scheduled job that calls the async function."""
    logger.info(f"Running scheduled job for thread: {thread_name}")
    asyncio.run(send_discord_message_trigger(thread_name))

def start_scheduler():
    """Starts the scheduler to run jobs at specified times."""
    logger.info("Starting scheduler...")
    for task in SCHEDULED_TASKS:
        schedule.every().day.at(task["schedule_time"]).do(job, task["thread_name"])
        logger.info(f"Scheduled task for thread '{task['thread_name']}' at {task['schedule_time']}.")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_scheduler()
