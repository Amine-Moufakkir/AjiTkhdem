from fastapi import FastAPI

app = FastAPI(title="AjiTkhdem - Ingestion API")

# @app.get("/")
# def read_root():
#     return {"status": "ok", "message": "Hello World from Ingestion Service!"}




if __name__ == "__main__":
    mes_proxies = ["192.168.1.1", "10.0.0.5"]
    mes_ua = ["Mozilla/5.0 (Windows NT 10.0)", "Mozilla/5.0 (Macintosh)"]

    mon_orchestrateur = Orchestrator()
    mon_scheduler = Scheduler(proxy_ips=mes_proxies, user_agents=mes_ua, orchestrator=mon_orchestrateur)

    # Le scheduler lance la mission
    mon_scheduler.schedule(site_name="amazon", url="https://amazon.fr/produit_test")
