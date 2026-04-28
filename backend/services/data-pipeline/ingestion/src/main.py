from fastapi import FastAPI
from orchestrator import Orchestrator
from scheduler import Scheduler

app = FastAPI(title="AjiTkhdem - IngestionService")

if __name__ == "__main__":
    # Target sites to scrape
    targets = [
        {"site": "rekrute", "url": "https://www.rekrute.com/offres.html"},
        {"site": "emploi.ma", "url": "https://www.emploi.ma/recherche-jobs-maroc"}
    ]

    orchestrateur = Orchestrator()
    
    # Pass the lists to the Scheduler
    scheduler = Scheduler(
        orchestrator=orchestrateur
    )

    # Run them one by one
    for target in targets:
        scheduler.schedule(site_name=target["site"], url=target["url"])