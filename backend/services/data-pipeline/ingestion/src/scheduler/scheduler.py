from src.orchestrator.orchestrator import Orchestrator
class Scheduler:
    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    def schedule(self, site_name: str, url: str):
        #ToRemove: Dev Mode
        print(f"--- Launching Job: {site_name} ---")
        scraper = self.orchestrator.create_scraper(
            site_name=site_name, 
            url=url
        )
        
        scraper.scrape()

    # schedule method for production
    #
    #
    # def schedule(self, site_name: str, url: str):
    #     # We pass a lambda that tells the scheduler: 
    #     # "When the timer hits, execute these two lines"
    #     self._scheduler.add_job(
    #         func=lambda: self.orchestrator.create_scraper(site_name, url).scrape(),
    #         trigger='interval',
    #         hours=4
    #     )
        
    #     self._scheduler.start()