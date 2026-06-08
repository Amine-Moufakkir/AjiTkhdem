import uuid
from typing import Optional, Any
from thefuzz import process
from core.BaseEntity import BaseEntity


class EntrepriseEntity(BaseEntity):
    """Représente une entreprise."""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        id  : Optional[str] = None,
        **kwargs
    ):
        self.id = id
        self.name = name
        self.description = description
        super().__init__(**kwargs)

    async def normalize(self, session: Optional[Any] = None) -> None:
        """Normalise les attributs de l'entreprise et effectue la résolution d'entité."""
        if isinstance(self.name, str):
            self.name = self.name.strip().lower()

        if session:
            from models.EntrepriseCrud import EntrepriseCRUD
            crud = EntrepriseCRUD(session)

            # 1. Vérifier si l'ID existe déjà en base
            if self.id:
                existing_by_id = await crud.get_by_id(self.id)
                if existing_by_id:
                    # On harmonise le nom avec celui en base
                    self.name = existing_by_id.name
                    return

            # 2. Vérifier si le nom exact existe déjà
            if self.name:
                existing_by_name = await crud.get_by_name(self.name)
                if existing_by_name:
                    self.id = existing_by_name.id
                    return

                # 3. Fuzzy matching si le nom exact n'existe pas
                similar_companies = await crud.search_by_name(self.name)
                if similar_companies:
                    names_map = {c.name: c for c in similar_companies}
                    best_match = process.extractOne(self.name, list(names_map.keys()))
                    
                    # Seuil de similarité (ex: 85%)
                    if best_match and best_match[1] >= 85:
                        matched_company = names_map[best_match[0]]
                        self.name = matched_company.name
                        self.id = matched_company.id
                        return

        # 4. Si pas d'ID (nouveau ou pas trouvé), on génère un hash random
        if not self.id:
            self.id = f"ent_{uuid.uuid4().hex[:8]}"


