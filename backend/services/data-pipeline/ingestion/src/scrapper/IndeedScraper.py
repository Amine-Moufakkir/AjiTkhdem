from scrapper.scrapper import AbstractScrapper

import asyncio
import logging
import random
from typing import List, Optional, Callable, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext  ,ViewportSize
from functools import partial

logger = logging.getLogger(__name__)


class RedisService:
    """
    Interface for Redis-based deduplication and storage.
    This is injected into IndeedScraper.
    """

    async def is_duplicate(self, job_id: str) -> bool:
        """Check if job ID exists."""
        raise NotImplementedError

    async def store(self, job_id: str) -> bool:
        """Store a new job ID."""
        raise NotImplementedError

 
class IndeedScraper(AbstractScrapper):
    """
    Lightweight async scraper for a single Indeed job search page.
    
    Features:
    - Single-page scraping (no pagination)
    - User agent randomization
    - Realistic browser context (viewport, locale, timezone)
    - Light stealth behavior (delay callbacks, scrolling)
    - Dependency injection for Redis interaction
    - Simple, modular design
    """

    # Realistic user agents to randomize
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]

    # Realistic viewport sizes
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
        {"width": 1280, "height": 800},
    ]

    def __init__(
        self,
        redis_service: RedisService,
        headless: bool = False,
        min_delay: float = 1.0,
        max_delay: float = 3.0,
    ):
        """browser


        Initialize the IndeedScraper.

        Args:
            redis_service: Injected RedisService for deduplication
            headless: Run browser in headless mode (default: False)
            min_delay: Minimum delay between actions in seconds (default: 1.0)
            max_delay: Maximum delay between actions in seconds (default: 3.0)
        """
        self.redis_service = redis_service
        self.headless = headless
        self.min_delay = min_delay
        self.max_delay = max_delay

        # Browser management
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Scraping state
        self.collected_job_ids: List[str] = []

        self.html_list: List[str] = []

        logger.info("IndeedScraper initialized")

    def _get_random_user_agent(self) -> str:
        """
        Select a random user agent from the predefined list.

        Returns:
            A realistic user agent string
        """
        return random.choice(self.USER_AGENTS)

    def _get_random_viewport(self) -> dict:
        """
        Select a random viewport size from the predefined list.

        Returns:
            A viewport dictionary with width and height
        """
                
        return random.choice(self.VIEWPORTS)

    async def _delay_with_callback(
        self,
        callback: Callable[[], Any],
        min_seconds: Optional[float] = None,
        max_seconds: Optional[float] = None,
    ) -> Any:
        """
        Apply a random delay before executing a callback.

        Args:
            callback: Async or sync function to execute after delay
            min_seconds: Minimum delay (uses instance default if None)
            max_seconds: Maximum delay (uses instance default if None)

        Returns:
            Result of the callback execution
        """
        min_sec = min_seconds if min_seconds is not None else self.min_delay
        max_sec = max_seconds if max_seconds is not None else self.max_delay

        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"Delaying {delay:.2f}s before action")
        await asyncio.sleep(delay)

        # Execute callback (handle both async and sync)
        if asyncio.iscoroutinefunction(callback):
            return await callback()
        else:
            return callback()

    async def _launch_browser(self) -> None:
        """
        Launch Playwright browser with stealth, user agent, and realistic context.
        """
        playwright = await async_playwright().start()

        # Launch with minimal flags to avoid detection
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
        )

        # Create context with realistic settings
        viewport = self._get_random_viewport()
        user_agent = self._get_random_user_agent()

        if not self.browser:
            raise RuntimeError("Failed to launch browser")

        #! On doit avoir une rotation des parameters ici  
        self.context = await self.browser.new_context(
            user_agent=user_agent,
            viewport=ViewportSize(width= viewport['width'] , height=viewport['height']), 
            locale="en-US",
            timezone_id="America/New_York",
        )

        if not self.context:
            raise RuntimeError("Failed to create browser context")

        self.page = await self.context.new_page()

        if not self.page:
            raise RuntimeError("Failed to create page")

        # Mask webdriver property
        await self.page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            """
        )

        logger.info(
            f"Browser launched: viewport={viewport['width']}x{viewport['height']}, "
            f"user_agent={user_agent[:50]}..."
        )

    async def _scroll_page(self, scroll_iterations: int = 2) -> None:
        """
        Perform light scrolling to simulate human behavior.

        Args:
            scroll_iterations: Number of scroll actions (default: 2)
        """
        if not self.page:
            logger.error("Page is not initialized")
            return

        for i in range(scroll_iterations):
            scroll_height = random.randint(300, 600)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_height})")

            # Small pause between scrolls
            await asyncio.sleep(random.uniform(0.5, 1.5))
            logger.debug(f"Scroll iteration {i + 1}/{scroll_iterations}")

    async def _extract_job_ids(self) -> List[str]:
        """
        Extract job IDs from the current page DOM.

        Looks for:
        - data-jk attribute
        - vjk parameter in job card elements

        Returns:
            List of extracted job IDs
        """
        if not self.page:
            logger.error("Page is not initialized")
            return []

        try:
            # Wait for job listings to load
            await self.page.wait_for_selector("[data-jk]", timeout=10000)

            job_ids = await self.page.evaluate(
                """
                () => {
                    const ids = [];
                    const jobCards = document.querySelectorAll('[data-jk]');
                    jobCards.forEach(card => {
                        const id = card.getAttribute('data-jk');
                        if (id && id.trim()) {
                            ids.push(id.trim());
                        }
                    });
                    return ids;
                }
                """
            )

            logger.info(f"Extracted {len(job_ids)} job IDs from page")
            return job_ids

        except Exception as e:
            logger.error(f"Error extracting job IDs: {e}")
            return []

    
        

    async def scrape(self, search_url: str) -> dict | None:
        """
        Scrape a single Indeed search page.

        Args:
            search_url: Complete Indeed search URL

        Returns:
            List of unique job IDs from the page
        """
        try:
            await self._launch_browser()

            if not self.page:
                raise RuntimeError("Browser page not initialized")

            logger.info(f"Starting scrape: {search_url}")

            # Navigate to the search page with delay
            async def navigate(search_url):
                page = self.page 
                if page is None : 
                    raise RuntimeError("La page n'est pas initialisée avant la navigation")
                await page.goto(search_url, wait_until="domcontentloaded" , timeout=60000)
                logger.info("Page loaded successfully")

                return await page.content()
            nav_func = partial(navigate, search_url)

            await self._delay_with_callback(nav_func, min_seconds=2.0, max_seconds=4.0)

            # Scroll to simulate human behavior
            await self._scroll_page(scroll_iterations=2)

            # Extract job IDs
            job_ids = await self._extract_job_ids()

            

            if not job_ids:
                logger.warning("No job IDs found on page")
                return None

            # Process 
            self.html_list  = []
            for job_id in job_ids:
             is_dup = await self.redis_service.is_duplicate(job_id)


            
             if is_dup:
                logger.debug(f"Job ID {job_id} is duplicate, skipping")
             else:
                
                new_url = f"https://ma.indeed.com/jobs?q=developpeur&l=Casablanca&start=0&vjk={job_id}&sort=date" 
                nav_jobs_function = partial(navigate , new_url)
                html = await self._delay_with_callback( nav_jobs_function, min_seconds=2.0, max_seconds=4.0)

                self.html_list.append(html)
                success = await self.redis_service.store(job_id)
                
                if success:
                    self.collected_job_ids.append(job_id)
                    logger.debug(f"Stored new job ID: {job_id}")
            
        

            #log
             logger.info(
                f"Scrape complete: extracted {len(job_ids)} IDs, "
                f"stored {len(self.collected_job_ids)} new IDs"
             )

        except Exception as e:
            logger.error(f"Scraping error: {e}", exc_info=True)
        finally:
            await self.close()

        return { "id_jobs" :  self.collected_job_ids  , "html_jobs":self.html_list }
 
    async def close(self) -> None:
        """Clean up browser resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Mock RedisService for testing
    class MockRedisService(RedisService):
        def __init__(self):
            self.stored_ids = set()

        async def is_duplicate(self, job_id: str) -> bool:
            return job_id in self.stored_ids

        async def store(self, job_id: str) -> bool:
            self.stored_ids.add(job_id)
            return True

    async def main():
        redis_service = MockRedisService()
        scraper = IndeedScraper(
            redis_service=redis_service,
            headless=False,
            min_delay=1.0,
            max_delay=3.0,
        )

        # Example search URL
        search_url = "https://ma.indeed.com/jobs?q=developpeur&l=Casablanca&start=0&sort=date"

        result  = await scraper.scrape(search_url)
        if result is not None  :
             jobs_ids = result["id_jobs"]
             html_list = result["html_jobs"]
             print("C'est la longueur du list d'html " , len(html_list))

         
      

             if html_list:
                # On définit le nom du fichier
                   filename = "test.html"
                
                # On ouvre le fichier en mode écriture ('w')
                # encoding="utf-8" est indispensable pour éviter les erreurs sur Linux
                   with open(filename, "w", encoding="utf-8") as f:
                    # On peut soit écrire tout le contenu d'un coup
                    # Ici, on va concaténer tous les HTML de la liste avec une séparation
                   
                       
                        f.write(html_list[0])
                        f.write("\n<hr>\n") # Ajoute une ligne de séparation entre les jobs
                
                   print(f"✅ Succès ! Le contenu a été écrit dans : {filename}")
             else:
                   print("⚠️ La liste HTML est vide, rien à écrire.")

    asyncio.run(main())

 






