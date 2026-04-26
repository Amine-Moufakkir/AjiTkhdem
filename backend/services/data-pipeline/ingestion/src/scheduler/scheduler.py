from orchestrator import Orchestrator
class Scheduler:
    def __init__(self, proxy_ips: list, user_agents: list, orchestrator: Orchestrator):
        self.proxy_ips = proxy_ips
        self.user_agents = user_agents
        self.orchestrator = orchestrator

    def schedule(self, site_name: str, url: str):
        print(f"--- Launching Job: {site_name} ---")
        
        # We pass the full lists down to the factory
        scraper = self.orchestrator.create_scraper(
            site_name=site_name, 
            url=url, 
            user_agents=self.user_agents, 
            proxy_ips=self.proxy_ips
        )
        
        scraper.scrape()