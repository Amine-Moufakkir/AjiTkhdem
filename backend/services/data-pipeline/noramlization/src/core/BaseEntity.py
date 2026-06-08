from abc import ABC, abstractmethod
from typing import Any, Dict




class BaseEntity(ABC):
    """
    Classe abstraite parent pour toutes les entités métier.
    Contient les comportements partagés et la logique commune de normalisation.
    """

    def __init__(self, **kwargs):
        """Initialise l'entité avec les attributs fournis."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    async def normalize(self, session: Any = None) -> None:
        """
        Normalise les attributs de l'entité.
        Chaque entité spécialise cette méthode selon ses besoins.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'entité en dictionnaire."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def __repr__(self) -> str:
        """Représentation textuelle de l'entité."""
        return f"{self.__class__.__name__}({self.to_dict()})"
    







