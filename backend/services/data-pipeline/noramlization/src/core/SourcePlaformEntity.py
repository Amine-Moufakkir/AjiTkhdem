from typing import Optional, Any
from core.BaseEntity import BaseEntity


class SourcePlatformEntity(BaseEntity):
    """Représente une plateforme source (ex: Indeed, LinkedIn)."""

    def __init__(
        self,
        name: str,
        id: Optional[int] = None,
        **kwargs
    ):
        self.id = id
        self.name = name
        super().__init__(**kwargs)

    async def normalize(self, session: Optional[Any] = None) -> None:
        """Normalise les attributs de la plateforme source et résout l'ID."""
        if isinstance(self.name, str):
            self.name = self.name.strip()

        if session and self.name:
            from models.SourcePlatformCrud import SourcePlatformCRUD
            crud = SourcePlatformCRUD(session)
            existing = await crud.get_by_name(self.name)
            if existing:
                self.id = existing.id
