import asyncio
import os
import sys
import time
import json
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from datetime import datetime, timezone
import uuid
# Monkey-patch de KafkaConsumer pour le test :
# 1. 'consumer_timeout_ms=5000' empêche le consommateur de bloquer indéfiniment.
# 2. 'group_id' unique garanti que le test lira toujours le message même si un autre service (ex: Docker) tourne.
import kafka
original_kafka_consumer = kafka.KafkaConsumer

class TestKafkaConsumer(original_kafka_consumer):
    def __init__(self, *args, **kwargs):
        kwargs['consumer_timeout_ms'] = 8000
        # On désactive le groupe pour éviter les bugs du coordinateur kafka-python
        kwargs['group_id'] = None
        super().__init__(*args, **kwargs)

    def subscribe(self, topics, *args, **kwargs):
        from kafka import TopicPartition
        tps = [TopicPartition(t, 0) for t in topics]
        print(f"[TestKafkaConsumer] Manual assignment aux partitions: {tps}")
        self.assign(tps)
        # On se place à la fin pour ne lire que notre nouveau message
        self.seek_to_end()

kafka.KafkaConsumer = TestKafkaConsumer
import src.kafka_client.KafkaClient as kafka_module
kafka_module.KafkaConsumer = TestKafkaConsumer

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
        
        # Création des topics avant de lancer les tests pour éviter les erreurs "not found in cluster metadata"
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
            existing_topics = admin_client.list_topics()
            
            topics_to_create = ["normalisation", "normalized_jobs"]
            for i in range(1, 6):
                topics_to_create.append(f"normalisation_retry_{i}")
                
            new_topics = []
            for t in topics_to_create:
                if t not in existing_topics:
                    # Configuration std: 1 partition, facteur de replication 1 (local Kafka)
                    new_topics.append(NewTopic(name=t, num_partitions=1, replication_factor=1))
                    
            if new_topics:
                print(f"[MockProducer] Création des topics manquants : {[t.name for t in new_topics]}")
                admin_client.create_topics(new_topics=new_topics, validate_only=False)
            
            admin_client.close()
        except Exception as e:
            print(f"[MockProducer] Avertissement: Impossible de créer les topics automatiquement ({e})")
            


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

    import threading
    
    # On définit une fonction pour envoyer le message dans un thread séparé
    def delayed_send():
        print("[Thread Produit] En attente de 2 secondes avant l'envoi...")
        time.sleep(2)
        try:
            print("[Thread Produit] Connexion au producteur...")
            producer = MockProducer()
            producer.send(topic="normalisation")
            print("[Thread Produit] Message envoyé !")
        except Exception as e:
            print(f"[Thread Produit] ✗ Erreur lors de l'envoi : {e}")

    # Lancement du thread producteur
    t = threading.Thread(target=delayed_send)
    t.daemon = True
    t.start()

    # Appel de la méthode main pour traiter le message (sur la boucle d'événements courante)
    print("Appel de la méthode main() pour la consommation (le thread principal va bloquer temporairement)...")
    try:
        # main() va bloquer la boucle d'événements pendant au maximum consumer_timeout_ms (5s)
        # s'il n'y a pas de message. Mais notre thread va envoyer un message après 2s !
        await main()
    except Exception as e:
        print(f"Erreur durant l'exécution de main() : {e}")

    # Vérification de la persistance en base de données
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
