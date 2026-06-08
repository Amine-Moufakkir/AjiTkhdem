from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.base import SourcePlatform

class SourcePlatformCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, platform_id: int) -> Optional[SourcePlatform]:
        stmt = select(SourcePlatform).where(SourcePlatform.id == platform_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[SourcePlatform]:
        stmt = select(SourcePlatform).where(SourcePlatform.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def insert(self, name: str) -> SourcePlatform:
        platform = SourcePlatform(name=name)
        self.session.add(platform)
        await self.session.commit()
        await self.session.refresh(platform)
        return platform
