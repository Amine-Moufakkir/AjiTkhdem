import os
import sys
import json

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
# Importation de ton contexte (ajuste le chemin si nécessaire)
from src.orchestrator.context import ScrapingContext
from src.orchestrator.orchestrator import Orchestrator

# Importation de ta classe RekruteScrapper
# Remplacer "nom_du_fichier" par le nom exact de ton fichier Python contenant la classe
from src.scrapper.RekruteScrapper import RekruteScrapper 

from src.orchestrator.context import ContextGenerator



# --- 1. FAUX CLIENT REDIS ---
# Simule Redis en utilisant un simple dictionnaire Python en mémoire
class DummyRedis:
    def __init__(self):
        self.storage = {}

    def exists(self, key: str) -> bool:
        # Renvoie True si le lien a déjà été "vu"
        return key in self.storage

    def setex(self, key: str, ttl: int, value: str):
        # Sauvegarde le lien en mémoire
        self.storage[key] = value
        print(f"[DummyRedis] Lien mis en cache : {key}")



# --- 2. FAUX PRODUCTEUR KAFKA ---
# Simule Kafka en affichant simplement ce qui aurait été envoyé
class DummyKafkaProducer:
    def produce(self, topic: str, key: str, value: str):
        print(f"[DummyKafka] 🟢 Message envoyé sur le topic '{topic}' | Clé: {key}")

    def flush(self):
        print("[DummyKafka] 🧹 Mémoire Kafka vidée (flush).")


# --- 3. EXÉCUTION DU TEST ---
if __name__ == "__main__":
    print("=== Démarrage du test manuel de RekruteScrapper ===")
    
    # Initialisation des fausses dépendances
    fake_redis = DummyRedis()
    fake_producer = DummyKafkaProducer()
    
    # Création d'un faux contexte (sans proxy pour être sûr que la requête passe depuis ta machine)
    use_proxy = os.getenv("USE_PROXY", "true").lower() not in {"false", "0", "no", "off"}

    print("use_proxy:", use_proxy)


    orchestrator = Orchestrator(
        redis_port=6379,
        kafka_bootstrap_servers="localhost:9092",
        use_proxy=use_proxy
    )
  
    fake_context = orchestrator._generate_context()

    # L'URL de base pour la recherche (à ajuster selon ton implémentation exacte)
    base_url = "https://www.rekrute.com/offres.html"
    
    # Instanciation de ton scraper
    print("\n[1] Initialisation du scraper...")
    scrapper =    orchestrator.create_scraper("Rekrute", "https://www.rekrute.com/offres.html")
    
    # Lancement de la méthode principale
    print("\n[2] Lancement de la méthode scrape()...\n")
    try:
        scrapper.scrape()
        print("\n=== Fin du test : SUCCÈS ===")
        
        # Test de simulation de la mémoire cache (Relancer une 2ème fois pour vérifier Redis)
        print("\n[3] Relance pour tester le comportement de la vérification Redis (déjà vu)...")
        scrapper.scrape()
        
    except Exception as e:
        print(f"\n=== Fin du test : ÉCHEC ===")
        print(f"Erreur rencontrée : {e}")