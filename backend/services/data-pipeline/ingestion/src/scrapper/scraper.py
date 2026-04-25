from abc import ABC, abstractmethod
from typing import List, Optional, Any

# ==========================================
# 1. Couche Scraper (Abstract & Factory)
# ==========================================

class AbstractScraper(ABC):
    def __init__(self, url: str, user_agent: str, ip: str):
        self._url = url  # Un seul underscore recommandé pour l'héritage
        self.user_agent = user_agent
        self.ip = ip
        
        # On les garde à None par défaut pour ne pas surcharger la mémoire.
        # La classe fille décidera d'initialiser celui dont elle a besoin.
        self.playwright_instance: Optional[Any] = None
        self.selenium_instance: Optional[Any] = None

    @abstractmethod
    def scrape(self):
        """Méthode que chaque site spécifique devra obligatoirement implémenter"""
        pass

# --- Exemples de classes concrètes (Héritage) ---

class AmazonScraper(AbstractScraper):
    def scrape(self):
        # Ici, on initialiserait Playwright par exemple
        print(f"Scraping d'Amazon sur {self._url} avec l'IP {self.ip}")

class WikipediaScraper(AbstractScraper):
    def scrape(self):
        # Ici, on pourrait utiliser Selenium
        print(f"Scraping de Wikipedia sur {self._url} avec le User-Agent {self.user_agent}")


# ==========================================
# 2. Couche Orchestrateur (Factory Pattern)
# ==========================================
