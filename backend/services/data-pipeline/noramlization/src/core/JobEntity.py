



from typing import Optional

from core.BaseEntity import BaseEntity


class JobEntity(BaseEntity):
    """Représente une offre d'emploi."""

    def __init__(
        self,
        hash_id: str,
        description: str,
        location: Optional[str] = None,
        profile: Optional[str] = None,
        salaire: Optional[float] = None,
        job_type : Optional[str] = None,
        entreprise_id: Optional[int] = None,
        source_platform_id: Optional[int] = None,
        apply_methode_id: Optional[int] = None,
        **kwargs
    ):
        self.hash_id = hash_id
        self.description = description
        self.location = location
        self.profile = profile
        self.salaire = salaire
        self.job_type = job_type
        self.entreprise_id = entreprise_id
        self.source_platform_id = source_platform_id
        self.apply_methode_id = apply_methode_id
        super().__init__(**kwargs)

    async def normalize(self, session: Optional[Any] = None) -> None:
        """Normalise les attributs de l'offre d'emploi."""
        if isinstance(self.description, str):
            self.description = self.description.strip().lower()
        if isinstance(self.profile, str):
            self.profile = self.profile.strip().lower()
        if isinstance(self.location, str):
            self.location = self.location.strip()
