from typing import Optional, Any
from core.BaseEntity import BaseEntity


class ApplyMethodeEntity(BaseEntity):
    """Représente une méthode de candidature (ex: email, formulaire web)."""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        id: Optional[int] = None,
        **kwargs
    ):
        self.id = id
        self.name = name
        self.description = description
        super().__init__(**kwargs)

    async def normalize(self, session: Optional[Any] = None) -> None:
        """Normalise les attributs de la méthode de candidature et résout l'ID."""
        if isinstance(self.name, str):
            self.name = self.name.strip()
        if isinstance(self.description, str):
            self.description = self.description.strip()

        if session and self.name:
            from models.ApplyMethodeCrud import ApplyMethodeCRUD
            crud = ApplyMethodeCRUD(session)
            existing = await crud.get_by_name(self.name)
            if existing:
                self.id = existing.id