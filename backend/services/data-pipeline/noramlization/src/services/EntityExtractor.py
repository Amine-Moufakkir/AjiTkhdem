from typing import Dict, Any, Optional

from core.ApplyMethodeEntity import ApplyMethodeEntity
from core.EntrepriseEntity import EntrepriseEntity
from core.JobEntity import JobEntity
from core.SourcePlaformEntity import SourcePlatformEntity


class EntityExtractor:
    """
    Classe responsable de l'extraction et de l'instanciation des entités
    à partir d'un dictionnaire brut représentant une offre d'emploi.
    """

    async def extract(self, data: Dict[str, Any], session: Optional[Any] = None) -> Dict[str, Any]:
        """
        Reçoit un dictionnaire brut, analyse les données,
        instancie les entités correspondantes et retourne une structure organisée.

        Args:
            data: Dictionnaire contenant les données brutes d'une offre d'emploi
            session: Session de base de données optionnelle pour la normalisation

        Returns:
            Dict contenant les entités instanciées organisées par table
        """
        entities = {}

        # Extraction de la plateforme source
        source_platform = await self._extract_source_platform(data, session)
        if source_platform:
            entities['source_platform'] = source_platform

        # Extraction de l'entreprise
        entreprise = await self._extract_entreprise(data, session)
        if entreprise:
            entities['entreprise'] = entreprise

        # Extraction de la méthode de candidature
        apply_methode = await self._extract_apply_methode(data, session)
        if apply_methode:
            entities['apply_methode'] = apply_methode

        # Extraction de l'offre d'emploi
        job = await self._extract_job(data, session)
        if job:
            entities['job'] = job

        return entities

    @staticmethod
    async def _extract_source_platform(data: Dict[str, Any], session: Optional[Any] = None) -> Optional[SourcePlatformEntity]:
        """Extrait et crée une entité SourcePlatform."""
        site = data.get('site')
        if not site:
            return None

        platform = SourcePlatformEntity(
            name=site,
            description=data.get('platform_description')
        )
        await platform.normalize(session)
        return platform

    @staticmethod
    async def _extract_entreprise(data: Dict[str, Any], session: Optional[Any] = None) -> Optional[EntrepriseEntity]:
        """Extrait et crée une entité Entreprise."""
        company = data.get('company')
        if not company:
            return None

        # Gestion si company est un dict ou une string
        ref = None
        name = None
        if isinstance(company, dict):
            ref = company.get('ref')
            name = company.get('name')
        else:
            name = company

        entreprise = EntrepriseEntity(
            id=ref,
            name=name,
            description=data.get('company_description')
        )
        await entreprise.normalize(session)
        return entreprise

    @staticmethod
    async def _extract_apply_methode(data: Dict[str, Any], session: Optional[Any] = None) -> Optional[ApplyMethodeEntity]:
        """Extrait et crée une entité ApplyMethode."""
        job_type = data.get('job_type')
        if not job_type:
            return None

        methode = ApplyMethodeEntity(
            name=job_type,
            description=data.get('apply_description')
        )
        await methode.normalize(session)
        return methode

    @staticmethod
    async def _extract_job(data: Dict[str, Any], session: Optional[Any] = None) -> Optional[JobEntity]:
        """Extrait et crée une entité Job."""
        description = data.get('job_description')
        if not description:
            return None

        job = JobEntity(
            hash_id=data.get('job_ref', ''),
            description=description,
            location=data.get('location'),
            profile=data.get('job_title'),
            salaire=data.get('salaire'),
            status=data.get('status', 'Open'),
            entreprise_id=data.get('entreprise_id'),
            source_platform_id=data.get('source_platform_id'),
            apply_methode_id=data.get('apply_methode_id'),
        )
        await job.normalize(session)
        return job



 