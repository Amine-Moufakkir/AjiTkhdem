
class Orchestrator:
    def __init__(self):
        # L'orchestrateur pourrait contenir d'autres logiques globales
        pass

    def create_scraper(self, site_name: str, url: str, user_agent: str, ip: str) -> AbstractScraper:
        """Méthode Factory qui instancie le bon scraper selon le site cible"""
        
        if site_name.lower() == "amazon":
            return AmazonScraper(url, user_agent, ip)
        elif site_name.lower() == "wikipedia":
            return WikipediaScraper(url, user_agent, ip)
        else:
            raise ValueError(f"Le scraper pour le site '{site_name}' n'existe pas.")

