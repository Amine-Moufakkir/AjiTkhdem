
from abc import ABC, abstractmethod

from core.HashGenerator import HashGenerator
from core.Cleaner import Cleaner
from models.db import MongoDB
from datetime import datetime

# --- Classes définies à l'extérieur (Ailleurs) ---


class GenericParser(ABC):
    def __init__(self , hash_generator: HashGenerator , db: MongoDB):
        # On instancie les classes définies ailleurs
        self.cleaner = Cleaner()
        self.hash_generator = hash_generator
        self.db = db  



    def __extract(self, raw_data: dict) -> dict:
        """Méthode privée d'extraction."""
        # Logique simulée : on pourrait imaginer une extraction de JSON ou RegEx ici
        return raw_data

    async def  pipeline(self, data: dict):
        """Méthode publique : le chef d'orchestre."""
        
        if data["html"] is None : 
             raise RuntimeError("Le contenu HTML de l'offre est vide") 
        
        cleaned_data = data  
        cleaned_data["html"] = self.cleaner.clean(data["html"])

        extracted = self.__extract(cleaned_data)
        
       
        
        # 3. Hachage
        hash_value = self.hash_generator.generate(extracted)
        

        meta_data = {
            "created_at":datetime.now(),
            "url":data["url"],
        }

        is_processed = await self.db.upsert_by_hash(hash_value, extracted , meta_data) 





#     @abstractmethod
#     def process(self, data_id: str, data: str):
#         """À implémenter dans les classes filles (ex: KafkaPublisher)."""
#         pass

# # --- Implémentation concrète ---

# class KafkaParser(GenericParser):
#     def process(self, data_id: str, data: str):
#         print(f"DEBUG: Envoi vers Kafka...")
#         print(f"ID: {data_id} | Payload: {data}")

# # Test
# if __name__ == "__main__":
#     p = KafkaParser()
#     p.pipeline("   donnée brute de kafka   ")