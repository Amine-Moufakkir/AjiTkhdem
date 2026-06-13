import asyncio
import logging
import sys
from orchestrator.orchestrator import Orchestrator
from scheduler.scheduler import Scheduler 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    # ToAdd: Move to configuration or .env
    sites_config = {
        "rekrute": "https://www.rekrute.com/offres.html",
        "indeed": "https://ma.indeed.com/jobs?q=developpeur&l=Casablanca"
    }

    logger.info("Initializing Data Pipeline Ingestion Service...")

    orchestrator = Orchestrator(
        redis_host="redis",
        redis_port=6379,
        kafka_bootstrap_servers="localhost:9092"
    )

    scheduler = Scheduler(
        orchestrator=orchestrator,
        sites_config=sites_config
    )

    # Start the scheduler
    scheduler.start()

    # Keep the main loop running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down service...")
        scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())