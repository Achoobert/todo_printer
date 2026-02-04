import logging
from threading import Thread
import time

from src.app import start as start_core_service
from src.bot import start_bot as start_discord_service
from src.scheduler import start_scheduler as start_schedule_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting all services...")

    # Start CORE SERVICE (Flask app) in a separate thread
    core_service_thread = Thread(target=start_core_service, daemon=True)
    core_service_thread.start()
    logger.info("CORE SERVICE started.")

    # Start DISCORD SERVICE (Bot and Flask app) in a separate thread
    discord_service_thread = Thread(target=start_discord_service, daemon=True)
    discord_service_thread.start()
    logger.info("DISCORD SERVICE started.")

    # Start SCHEDULE SERVICE in a separate thread
    schedule_service_thread = Thread(target=start_schedule_service, daemon=True)
    schedule_service_thread.start()
    logger.info("SCHEDULE SERVICE started.")

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down all services...")

if __name__ == "__main__":
    main()
