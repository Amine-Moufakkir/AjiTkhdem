from fastapi import FastAPI
from orchestrator import Orchestrator
from scheduler import Scheduler

app = FastAPI(title="AjiTkhdem - Ingestion API")

if __name__ == "__main__":
    # Your raw data lists
    proxies = ["192.168.1.1", "10.0.0.5"]
    user_agents = ["Mozilla/5.0 (Windows NT 10.0)", "Mozilla/5.0 (Macintosh)"]

    # Target sites to scrape
    targets = [
        {"site": "rekrute", "url": "https://www.rekrute.com/offres.html"},
        {"site": "emploi.ma", "url": "https://www.emploi.ma/recherche-jobs-maroc"}
    ]

    mon_orchestrateur = Orchestrator()
    
    # Pass the lists to the Scheduler
    mon_scheduler = Scheduler(
        proxy_ips=proxies, 
        user_agents=user_agents, 
        orchestrator=mon_orchestrateur
    )

    # Run them one by one
    for target in targets:
        mon_scheduler.schedule(site_name=target["site"], url=target["url"])