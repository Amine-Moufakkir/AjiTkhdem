import random
import logging
import asyncio
from datetime import datetime, time, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from orchestrator.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

class Scheduler:
    """
    Responsible for scheduling web scraping tasks at randomized time intervals
    and within specific time windows to mimic human behavior and avoid detection.
    """
    def __init__(self, orchestrator: Orchestrator, sites_config: dict[str, str]):
        self.orchestrator = orchestrator
        self.sites_config = sites_config
        self.scheduler = AsyncIOScheduler()

        # Default window: 08:00 to 22:00
        self.window_start = time(8, 0)
        self.window_end = time(22, 0)

        logger.info(f"Scheduler initialized with window {self.window_start} - {self.window_end}")

    def is_within_window(self) -> bool:
        """Checks if the current time is within the allowed scraping window."""
        current_time = datetime.now().time()
        is_inside = self.window_start <= current_time <= self.window_end
        if not is_inside:
            logger.debug(f"Current time {current_time} is outside window {self.window_start}-{self.window_end}")
        return is_inside

    async def _run_session(self):
        """Wrapper to run a scraping session if within window and then schedule the next one."""
        if not self.is_within_window():
            logger.info("Outside of allowed window. Skipping this run.")
        else:
            try:
                site_name, url = self.orchestrator.select_next_site(self.sites_config)
                logger.info(f"Starting scheduled session for {site_name}")
                await self.orchestrator.run_scraping_session(site_name, url)
            except Exception as e:
                logger.error(f"Error in scheduled job: {e}")

        # Always schedule the next run to maintain the loop
        self._schedule_next()

    def _schedule_next(self):
        """Schedules the next execution at a randomized interval."""
        # Random interval between 30 and 120 minutes
        minutes = random.randint(30, 120)
        run_date = datetime.now() + timedelta(minutes=minutes)

        self.scheduler.add_job(
            self._run_session,
            trigger='date',
            run_date=run_date,
            id='scraping_job',
            replace_existing=True
        )
        logger.info(f"Next session scheduled for {run_date.strftime('%H:%M:%S')} (in {minutes} minutes)")

    def start(self):
        """Starts the scheduler and triggers the first job."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started.")
            # Start the first run immediately
            self.scheduler.add_job(self._run_session, trigger='date', run_date=datetime.now())
        else:
            logger.warning("Scheduler is already running.")

    def stop(self):
        """Stops the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped.")