

# ==========================================
# 3. Couche Scheduler
# ==========================================

from typing import List


class Scheduler:
    def __init__(self, proxy_ips: List[str], user_agents: List[str], orchestrator: Orchestrator):
        self.proxy_ips = proxy_ips
        self.user_agents = user_agents
        self.orchestrator = orchestrator

    def schedule(self, site_name: str, url: str):
        """
        Logique pour sélectionner une IP et un User-Agent, 
        puis demander à l'orchestrateur de lancer le job.
        """
        # Exemple basique : on prend le premier de la liste (il faudra une vraie logique de rotation)
        selected_ip = self.proxy_ips[0] if self.proxy_ips else "127.0.0.1"
        selected_ua = self.user_agents[0] if self.user_agents else "Default-User-Agent"

        print("--- Début du Job par le Scheduler ---")
        
        # L'orchestrateur fabrique le scraper
        scraper = self.orchestrator.create_scraper(
            site_name=site_name, 
            url=url, 
            user_agent=selected_ua, 
            ip=selected_ip
        )
        
        # On exécute le scraping
        scraper.scrape()
