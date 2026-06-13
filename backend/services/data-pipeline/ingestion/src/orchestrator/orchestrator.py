import random
import redis
import logging
import asyncio
from confluent_kafka import Producer
from scrapper.scrapper import AbstractScrapper, resolve_use_proxy
from scrapper.RekruteScrapper import RekruteScrapper
from scrapper.IndeedScraper import IndeedScraper
from .context import ContextGenerator, ScrapingContext

logger = logging.getLogger(__name__)


class IndeedRedisWrapper:
    """Wraps redis client to provide methods expected by IndeedScraper."""
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.TTL = 48 * 60 * 60

    async def is_duplicate(self, job_id: str) -> bool:
        # Standard redis is sync, but we use it in async context
        return self.redis.exists(f"indeed:seen:{job_id}")

    async def store(self, job_id: str) -> bool:
        self.redis.setex(f"indeed:seen:{job_id}", self.TTL, "1")
        return True


class Orchestrator:
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        kafka_bootstrap_servers: str = "localhost:9092",
        min_delay: float = 1.0,
        max_delay: float = 3.0,
        use_proxy: bool = True,
        useProxy: bool | None = None,
    ):
        self.use_proxy = resolve_use_proxy(use_proxy=use_proxy, useProxy=useProxy)
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            decode_responses=True,
        )

        kafka_conf = {
            "bootstrap.servers": kafka_bootstrap_servers,
            "client.id": "ingestion-service",
            "reconnect.backoff.ms": 1000,
            "reconnect.backoff.max.ms": 10000,
        }
        self.kafka_producer = Producer(kafka_conf)
        self.context_generator = ContextGenerator(min_delay=min_delay, max_delay=max_delay)

    def _generate_context(self) -> ScrapingContext:
        return self.context_generator.generate()

    def create_scraper(self, site_name: str, url: str) -> AbstractScrapper:
        name = site_name.lower()
        context = self._generate_context()

        if name == "rekrute":
            scraper = RekruteScrapper(
                redis_client=self.redis_client,
                kafka_producer=self.kafka_producer,
                base_url=url,
                context=context,
                use_proxy=self.use_proxy
            )
            return scraper
        elif name == "indeed":
            scraper = IndeedScraper(
                redis_service=IndeedRedisWrapper(self.redis_client),
                headless=True,
                min_delay=context.min_delay,
                max_delay=context.max_delay,
                context=context,
                use_proxy=self.use_proxy
            )
            return scraper
        else:
            raise ValueError(f"Le scraper pour le site '{site_name}' n'existe pas.")

    def select_next_site(self, sites_config: dict[str, str]) -> tuple[str, str]:
        """
        Selects the next site to scrape from the available configurations.
        Decision-making can be randomized or based on priority/load.
        """
        if not sites_config:
            raise ValueError("No sites available for scraping")

        site_name = random.choice(list(sites_config.keys()))
        url = sites_config[site_name]
        return site_name, url

    async def run_scraping_session(self, site_name: str, url: str) -> dict:
        """
        Executes a scraping session for a specific site.
        Handles both sync and async scrapers.
        """
        scraper = self.create_scraper(site_name=site_name, url=url)
        context = scraper.context
        logger.info(f"Running scraper for {site_name} with context: UA={context.user_agent[:50]}...")

        try:
            if asyncio.iscoroutinefunction(scraper.scrape) or asyncio.iscoroutine(scraper.scrape):
                await scraper.scrape(url) if site_name.lower() == "indeed" else await scraper.scrape()
            else:
                # If the scraper.scrape is not a coroutine function but it returns a coroutine
                result = scraper.scrape(url) if site_name.lower() == "indeed" else scraper.scrape()
                if asyncio.iscoroutine(result):
                    await result
        except Exception as e:
            logger.error(f"Error during scraping session for {site_name}: {e}")
            return {"site": site_name, "status": "failed", "error": str(e)}

        return {"site": site_name, "status": "completed"}