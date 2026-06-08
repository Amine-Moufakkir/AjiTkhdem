from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.base import Job

class JobCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_hash_id(self, hash_id: str) -> Optional[Job]:
        stmt = select(Job).where(Job.hash_id == hash_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def insert(self, **kwargs) -> Job:
        job = Job(**kwargs)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def update_by_hash_id(self, hash_id: str, **kwargs) -> Optional[Job]:
        stmt = select(Job).where(Job.hash_id == hash_id)
        result = await self.session.execute(stmt)
        job = result.scalar_one_or_none()
        if job:
            for key, value in kwargs.items():
                setattr(job, key, value)
            await self.session.commit()
            await self.session.refresh(job)
        return job
