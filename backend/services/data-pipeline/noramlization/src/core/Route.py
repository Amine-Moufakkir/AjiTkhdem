from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from services.NormalisationService import NormalizationService
from services.EntityExtractor import EntityExtractor
from models.SourcePlatformCrud import SourcePlatformCRUD
from models.ApplyMethodeCrud import ApplyMethodeCRUD
from models.EntrepriseCrud import EntrepriseCRUD
from models.JobCrud import JobCRUD


class Route:
    """
    Classe principale encapsulant le pipeline de normalisation et d'extraction.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.normalization_service = NormalizationService()
        self.entity_extractor = EntityExtractor()

    async def normalise_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute le pipeline complet :
        1. Normalisation brute des données.
        2. Extraction des entités métier.
        3. Persistance (insertion ou mise à jour) en respectant les relations.
        """
        # 1. Normalisation brute
        normalized_data = self.normalization_service.normalize(data)

        # 2. Extraction des entités (et résolution initiale si session fournie)
        entities = await self.entity_extractor.extract(normalized_data, self.session)

        # 3. Persistance en respectant l'ordre des relations
        # a. Source Platform
        source_platform_entity = entities.get('source_platform')
        if source_platform_entity and not source_platform_entity.id:
            crud = SourcePlatformCRUD(self.session)
            db_obj = await crud.insert(name=source_platform_entity.name)
            source_platform_entity.id = db_obj.id

        # b. Apply Methode
        apply_methode_entity = entities.get('apply_methode')
        if apply_methode_entity and not apply_methode_entity.id:
            crud = ApplyMethodeCRUD(self.session)
            db_obj = await crud.insert(
                name=apply_methode_entity.name, 
                description=apply_methode_entity.description
            )
            apply_methode_entity.id = db_obj.id

        # c. Entreprise
        entreprise_entity = entities.get('entreprise')
        if entreprise_entity:
            crud = EntrepriseCRUD(self.session)
            # On vérifie si elle existe déjà (au cas où normalize ne l'a pas fait ou si on veut forcer l'insert)
            existing = await crud.get_by_id(entreprise_entity.id)
            if not existing:
                db_obj = await crud.insert(
                    id=entreprise_entity.id,
                    name=entreprise_entity.name,
                    description=entreprise_entity.description
                )
            else:
                # Optionnel: Update si nécessaire
                await crud.update_by_id(
                    entreprise_entity.id,
                    new_name=entreprise_entity.name,
                    new_description=entreprise_entity.description
                )

        # d. Job
        job_entity = entities.get('job')
        if job_entity:
            # Lier les IDs résolus
            if source_platform_entity:
                job_entity.source_platform_id = source_platform_entity.id
            if apply_methode_entity:
                job_entity.apply_methode_id = apply_methode_entity.id
            if entreprise_entity:
                job_entity.entreprise_id = entreprise_entity.id

            crud = JobCRUD(self.session)
            existing_job = await crud.get_by_hash_id(job_entity.hash_id)
            
            job_data = job_entity.to_dict()
            if not existing_job:
                await crud.insert(**job_data)
            else:
                await crud.update_by_hash_id(job_entity.hash_id, **job_data)

        return entities
