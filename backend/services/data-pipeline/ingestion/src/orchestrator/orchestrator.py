from scrapper import AbstractScraper
from scrapper import RekruteScraper   
class Orchestrator:
    def __init__(self):
        # Could hold global config or shared sessions if needed later
        pass

    def create_scraper(self, site_name: str, url: str, user_agents: list, proxy_ips: list) -> AbstractScraper:
        """
        Factory Method: Injects the full lists into the scraper so it 
        can handle its own internal rotation.
        """
        
        name = site_name.lower()
        
        if name == "rekrute":
            return RekruteScraper(url, user_agents, proxy_ips)
        # To add other scrapers later, just add more conditions here
        else:
            raise ValueError(f"Le scraper pour le site '{site_name}' n'existe pas.")