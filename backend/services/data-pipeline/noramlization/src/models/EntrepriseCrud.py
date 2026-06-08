

from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.base import Entreprise


class EntrepriseCRUD:
    def __init__(self, session: AsyncSession):
        """On injecte la session asynchrone à l'instanciation"""
        self.session = session

    # 🔎 1. RECHERCHE PAR ID
    async def get_by_id(self, entreprise_id: str) -> Optional[Entreprise]:
        """Trouve une entreprise par son ID."""
        stmt = select(Entreprise).where(Entreprise.id == entreprise_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # 🔎 2. RECHERCHE PAR NOM EXACT
    async def get_by_name(self, name: str) -> Optional[Entreprise]:
        """Trouve une entreprise par son NOM exact."""
        stmt = select(Entreprise).where(Entreprise.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # 🔎 3. RECHERCHE (LIKE '%string%')
    async def search_by_name(self, query: str) -> Sequence[Entreprise]:
        """
        Liste les entreprises dont le nom contient la chaîne 'query'.
        Note: On utilise .ilike() pour que la recherche ignore la casse (PostgreSQL).
         Si tu veux que ce soit sensible à la casse, utilise .like()
        """
        stmt = select(Entreprise).where(Entreprise.name.ilike(f"%{query}%"))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ➕ 4. INSERTION
    async def insert(self, name: str, description: Optional[str] = None, id: Optional[str] = None) -> Entreprise:
        """Crée et insère une nouvelle entreprise en base de données."""
        nouvelle_entreprise = Entreprise(name=name, description=description, id=id)
        
        self.session.add(nouvelle_entreprise)
        await self.session.commit()
        await self.session.refresh(nouvelle_entreprise)
        
        return nouvelle_entreprise

    # 🔄 5. MISE À JOUR PAR ID
    async def update_by_id(self, entreprise_id: str, new_name: Optional[str] = None, new_description: Optional[str] = None) -> Optional[Entreprise]:
        """Trouve une entreprise par son ID et met à jour ses champs."""
        # On récupère d'abord l'entité
        stmt = select(Entreprise).where(Entreprise.id == entreprise_id)
        result = await self.session.execute(stmt)
        entreprise = result.scalar_one_or_none()
        
        if entreprise:
            if new_name is not None:
                entreprise.name = new_name
            if new_description is not None:
                entreprise.description = new_description
                
            await self.session.commit()
            await self.session.refresh(entreprise)
            
        return entreprise

    # 🔄 4. MISE À JOUR PAR NOM
    async def update_by_name(self, current_name: str, new_name: Optional[str] = None, new_description: Optional[str] = None) -> Optional[Entreprise]:
      """Trouve une entreprise par son NOM actuel et met à jour ses champs."""
      stmt = select(Entreprise).where(Entreprise.name == current_name)
      result = await self.session.execute(stmt)
      entreprise = result.scalar_one_or_none()
      
      # On vérifie simplement si l'entreprise existe
      if entreprise:
          if new_name is not None:
              entreprise.name = new_name
          if new_description is not None:
              entreprise.description = new_description
              
          await self.session.commit()
          await self.session.refresh(entreprise)
          
      return entreprise