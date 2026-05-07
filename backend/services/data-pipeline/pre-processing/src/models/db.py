import os
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

from config.MongoConnection import MongoConnection

load_dotenv()


class MongoDB:
    """
    Gestion des documents dans MongoDB avec recherche par hash.
    """
    
    def __init__(self, mongo_connection: MongoConnection, collection_name: str = "raw_data"):
        """
        Args:
            mongo_connection: Instance de MongoConnection
            collection_name: Nom de la collection à interroger
        """
        self.mongo = mongo_connection
        self.collection_name = collection_name
    
    async def find_by_hash(self, hash_value: str) -> Optional[Dict[str, Any]]:
        """
        Recherche un document par son hash.
        
        Args:
            hash_value: Le hash à rechercher
            
        Returns:
            Le document trouvé ou None
        """
        collection = self.mongo.get_collection(self.collection_name)
        document = await collection.find_one({"hash": hash_value})
        return document
    
    async def find_by_hash_in_field(self, hash_value: str, field_name: str = "hash") -> Optional[Dict[str, Any]]:
        """
        Recherche un document par hash dans un champ spécifique.
        
        Args:
            hash_value: Le hash à rechercher
            field_name: Nom du champ contenant le hash
            
        Returns:
            Le document trouvé ou None
        """
        collection = self.mongo.get_collection(self.collection_name)
        document = await collection.find_one({field_name: hash_value})
        return document
    
    async def exists(self, hash_value: str, field_name: str = "hash") -> bool:
        """
        Vérifie si un document avec ce hash existe.
        
        Args:
            hash_value: Le hash à vérifier
            field_name: Nom du champ contenant le hash
            
        Returns:
            True si le document existe
        """
        document = await self.find_by_hash_in_field(hash_value, field_name)
        return document is not None
    
    async def find_all_by_hashes(self, hash_values: List[str], field_name: str = "hash") -> List[Dict[str, Any]]:
        """
        Recherche plusieurs documents par leurs hashs.
        
        Args:
            hash_values: Liste des hashs à rechercher
            field_name: Nom du champ contenant le hash
            
        Returns:
            Liste des documents trouvés
        """
        collection = self.mongo.get_collection(self.collection_name)
        cursor = collection.find({field_name: {"$in": hash_values}})
        documents = await cursor.to_list(length=None)
        return documents
    
    async def find_duplicate(self, job_ref: str, company_ref: str, site: str) -> Optional[Dict[str, Any]]:
        """
        Recherche un doublon par ses composants (sans avoir le hash).
        
        Args:
            job_ref: Référence du job
            company_ref: Référence de l'entreprise
            site: Site source
            
        Returns:
            Document en doublon ou None
        """
        collection = self.mongo.get_collection(self.collection_name)
        document = await collection.find_one({
            "job_ref": job_ref,
            "company_ref": company_ref,
            "site": site
        })
        return document
    
    async def upsert_by_hash(self, hash_value: str, data: Dict[str, Any] , metadata: Dict[str, Any]) -> bool:
        """
        Met à jour ou insère un document selon son hash.
        
        - Si le document n'existe pas : l'insère et retourne True
        - Si le document existe et est identique : ne fait rien et retourne false
        - Si le document existe mais différent : le met à jour et retourne true

        
        Args:
            hash_value: Le hash du document
            data: Les données du document (doit contenir le champ 'hash')
            
        Returns:
            True si le document est à jour (existe et identique ou nouvellement inséré)
            False si le document a été mis à jour (existant mais modifié)
        """
        collection = self.mongo.get_collection(self.collection_name)
        
        # Ajouter le hash aux données si pas déjà présent
        data["hash"] = hash_value
        
        # Vérifier si le document existe déjà
        existing_doc = await self.find_by_hash(hash_value)
        
        if existing_doc is None:
            # Le document n'existe pas, on l'insère
            self._add_metadata(data ,metadata )
            await collection.insert_one(data)
            return True
        
        # Le document existe, comparer les champs
        if self._compare_documents(existing_doc, data):
            # Documents identiques, rien à faire
            return False
        else:
            # Documents différents, mise à jour
            data["updated_at"] = datetime.now()
            await collection.update_one(
                {"hash": hash_value},
                {"$set": data}
            )
            return True
    
    def _compare_documents(self, doc1: Dict[str, Any], doc2: Dict[str, Any], ignore_fields: List[str] = []) -> bool:
        """
        Compare deux documents en ignorant certains champs.
        
        Args:
            doc1: Premier document
            doc2: Deuxième document
            ignore_fields: Liste des champs à ignorer (_id, created_at, etc.)
            
        Returns:
            True si les documents sont identiques
        """
        if ignore_fields is None:
            ignore_fields = ["_id", "created_at", "updated_at"]
        
        # Filtrer les champs à ignorer
        doc1_filtered = {k: v for k, v in doc1.items() if k not in ignore_fields}
        doc2_filtered = {k: v for k, v in doc2.items() if k not in ignore_fields}
        
        return doc1_filtered == doc2_filtered
    

    def _add_metadata(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
     """
     Ajoute des métadonnées au document.
     
     Args:
         data: Le document de base
         metadata: Dictionnaire des métadonnées à ajouter
         
     Returns:
         Le document enrichi avec les métadonnées
     """
     data["metadata"] = metadata
     return data




