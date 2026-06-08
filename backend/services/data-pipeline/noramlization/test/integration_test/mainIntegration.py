import asyncio
import os
import sys
import time
import json
from kafka import KafkaProducer
from datetime import datetime, timezone
import uuid
from src.config.db import AsyncSessionLocal, engine
from src.models.base import Base, Entreprise, Job
from src.main import main


from sqlalchemy import select

class MockProducer:
    """
    Simule un producteur pour le test, mais envoie des messages réels à Kafka.
    """
    def __init__(self, bootstrap_servers=None):
        # On récupère l'adresse du broker Kafka depuis l'environnement ou par défaut
        self.bootstrap_servers = bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        print(f"[MockProducer] Connexion au broker Kafka sur {self.bootstrap_servers}...")
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )


    def send(self, topic, message=None):
        """
        Envoie un message vers Kafka. Si aucun message n'est fourni,
        génère un payload mocké pour les tests de l'offre d'emploi.
        """
        
        # 1. Génération des données de test si 'message' est vide
        if message is None:
            message = {
                "site": "linkedin.com",
                "job_title": "Data Engineer Python",
                "job_ref": "JOB-2024-001",
                "company": {
                    "name": "Tech Solutions SAS",
                    "ref": "COMP-789"
                },
                "location": "paris",
                "job_type": "CDI",
                "job_description": "Nous recherchons un développeur pour notre pipeline Kafka...",
                "url": "https://example.com/jobs/job-2024-001",
                "hash": str(uuid.uuid4()),  # Génère un hash unique pour le test
                
                # Conversion obligatoire des dates en chaînes de caractères pour le JSON
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

        print(f"[MockProducer] Envoi du message au topic : {topic}")
        
        # 2. Envoi du message (Le value_serializer de KafkaConsumer convertira ce dict en JSON)
        future = self.producer.send(topic, value=message)
        self.producer.flush()
        
        print("[MockProducer] Message envoyé et flushé.")
        return future
async def run_test():
    print("=== Démarrage du test d'intégration (Kafka Réel) ===")

    # 1. Vérification de la connexion à la base de données
    print(f"Vérification de la connexion à la base de données (engine: {engine.url})...")


    try:
        async with engine.begin() as conn:
            print("✓ Connexion à la base de données réussie.")
            # On s'assure que les tables existent
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"✗ Erreur de connexion à la base de données : {e}")
        return False

    # 2. Préparation du message de test
    
    # 3. Utilisation du MockProducer pour envoyer le message au topic réel
    try:
        producer = MockProducer()
        producer.send( topic = "normalisation")
    except Exception as e:
        print(f"✗ Erreur lors de l'envoi au broker Kafka : {e}")
        print("Vérifiez que le serveur Kafka est accessible.")
        return False

    # 4. Attente de 2 secondes pour laisser le temps au broker de traiter
    print("Attente de 2 secondes...")
    await asyncio.sleep(2)

    # 5. Appel de la méthode main pour traiter le message
    # main() est une boucle infinie de consommation Kafka, on lui donne un timeout
    print("Appel de la méthode main() pour la consommation (Timeout 15s)...")
    try:
        # On lance le service de normalisation réel
        await asyncio.wait_for(main(), timeout=15)
    except asyncio.TimeoutError:
        print("Fin du temps imparti pour le traitement (Timeout atteint, c'est normal).")
    except Exception as e:
        print(f"Erreur durant l'exécution de main() : {e}")
        # On ne s'arrête pas forcément ici si c'est juste un arrêt propre

    # 6. Vérification de la persistance en base de données
    print("Vérification de la base de données...")
    async with AsyncSessionLocal() as session:
        # Recherche de l'entreprise créée
        result_ent = await session.execute(
            select(Entreprise).where(Entreprise.name == "Tech Solutions SAS")
        )
        entreprise = result_ent.scalar_one_or_none()
        
        if entreprise:
            print(f"✓ Entreprise trouvée en DB : {entreprise.name}")
            
            # Recherche du job lié
            result_job = await session.execute(
                select(Job).where(Job.entreprise_id == entreprise.id)
            )
            job = result_job.scalar_one_or_none()
            
            if job:
                print(f"✓ Job trouvé en DB pour l'entreprise {entreprise.name}")
                print(f"  ID Job : {job.hash_id}")
                print(f"  Description : {job.description[:50]}...")
            else:
                print("✗ Job non trouvé en base de données.")
                return False
        else:
            print("✗ Entreprise non trouvée en base de données.")
            return False

    print("=== Test d'intégration réussi avec Kafka réel ! ===")
    return True

if __name__ == "__main__":
    # Lancement du test
    try:
        success = asyncio.run(run_test())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nTest interrompu par l'utilisateur.")
        sys.exit(0)
