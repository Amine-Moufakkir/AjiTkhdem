from abc import ABC
from typing import Any
from core.HashPatternGenerator import HashPatternGenerator
from genericParser import GenericParser
from core.HashGenerator import HashGenerator
from models.db import MongoDB
from services.IndeedParser import IndeedParser



class ParserFactory:
    """Factory class pour créer des instances de GenericParser."""
    
    def __init__(self,  db: MongoDB):
        self.db = db
        
    # def register_parser(self, parser_type: str, parser_class):
    #     """Enregistre un type de parser."""
    #     self._parsers[parser_type.lower()] = parser_class

    def getMongoDb(self, ) -> Any:
        return self.db
    
    def build_parser(self, parser_type: str) -> GenericParser:
        """
        Crée et retourne une instance de GenericParser selon le type spécifié.
        
        Args:
            parser_type: Type de parser à créer (string)
            
        Returns:
            GenericParser: Instance du parser demandé
            
        Raises:
            ValueError: Si le type de parser n'existe pas
        """
        parser_type_lower = parser_type.lower()
        
        if parser_type_lower == "indeed":
            hash_generator = HashPatternGenerator()
            return IndeedParser(  hash_generator , self.db)
        
        else :
            raise ValueError(f"Le type de parser '{parser_type}' n'est pas enregistré.")
       




