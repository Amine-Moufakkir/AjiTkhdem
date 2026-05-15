import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class MongoConnection:
    def __init__(self):
        
        
        self.uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGO_DB_NAME", "job-scraper")
        self.client = None
        self.db = None

    async def connect(self):
        """Établit la connexion à MongoDB."""
        if not self.client:
            try:
                self.client = AsyncIOMotorClient(self.uri)
                self.db = self.client[self.db_name]
                print(f"Connecté à MongoDB : {self.db_name}")
            except Exception as e:
                print(f"Erreur de connexion MongoDB : {e}")

    def get_collection(self, collection_name="raw_data"):
        """Récupère une collection spécifique."""
        if self.db is None:
            raise Exception("La connexion à la base de données n'est pas établie. Appelez connect() d'abord.")
        return self.db[collection_name]

    async def close(self):
        """Ferme la connexion MongoDB."""
        if self.client:
            self.client.close()
            print("Connexion MongoDB fermée.")
