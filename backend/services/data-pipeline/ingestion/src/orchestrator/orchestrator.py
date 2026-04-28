from scrapper import AbstractScraper
from scrapper import RekruteScraper   
class Orchestrator:
    def __init__(self):
        pass

    def create_scraper(self, site_name: str, url: str) -> AbstractScraper:        
        name = site_name.lower()
        
        if name == "rekrute":
            return RekruteScraper(url)
        # To add other scrapers later, just add more conditions here
        else:
            raise ValueError(f"Le scraper pour le site '{site_name}' n'existe pas.")