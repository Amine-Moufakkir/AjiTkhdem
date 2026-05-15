
from __future__ import annotations # Pour accepter le type | None sans erreur
from abc import ABC, abstractmethod

from core.HashGenerator import HashGenerator
from core.Cleaner import Cleaner
from dto.DataProcessingDTO import DataProcessingDTO
from dto.JobCleanedDTO import JobCleanedDTO
from models.db import MongoDB
from datetime import datetime

# --- Classes définies à l'extérieur (Ailleurs) ---


class GenericParser(ABC):
    def __init__(self , hash_generator: HashGenerator , db: MongoDB):
        # On instancie les classes définies ailleurs
        self.cleaner = Cleaner()
        self.hash_generator = hash_generator
        self.db = db  



    def __extract(self, raw_data:DataProcessingDTO ) -> JobCleanedDTO | None:
        """Méthode privée d'extraction."""
        # Logique simulée : on pourrait imaginer une extraction de JSON ou RegEx ici
        return JobCleanedDTO() 

    async def  pipeline(self, data: DataProcessingDTO) ->JobCleanedDTO | None:
        """Méthode publique : le chef d'orchestre."""
        
        if data.html is None : 
             raise RuntimeError("Le contenu HTML de l'offre est vide") 
         
        cleaned_data = data 
        cleaned_data.html = self.cleaner.clean(data.html)

        extracted = self.__extract(cleaned_data)
        # Retourne un JobCleanedDTO

        
        if extracted is None:
            raise RuntimeError("Extraction de l'offre d'emploi impossible")
        dict_extracted = extracted.to_dict()
        
       
        
        # 3. Hachage
        hash_value = self.hash_generator.generate(dict_extracted)
        

        meta_data = {
            "created_at":datetime.now(),
            "url":data.url,
        }

        is_processed = await self.db.upsert_by_hash(hash_value, dict_extracted , meta_data) 

        if is_processed:
            return extracted 
        return None