from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.base import ApplyMethode

class ApplyMethodeCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, methode_id: int) -> Optional[ApplyMethode]:
        stmt = select(ApplyMethode).where(ApplyMethode.id == methode_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[ApplyMethode]:
        stmt = select(ApplyMethode).where(ApplyMethode.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def insert(self, name: str, description: Optional[str] = None) -> ApplyMethode:
        methode = ApplyMethode(name=name, description=description)
        self.session.add(methode)
        await self.session.commit()
        await self.session.refresh(methode)
        return methode
