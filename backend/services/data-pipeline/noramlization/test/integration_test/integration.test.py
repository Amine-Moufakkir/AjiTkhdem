import pytest
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv

from core.Route import Route
from models.base import Base, Entreprise, Job, SourcePlatform, ApplyMethode
import pytest_asyncio

# Load env for database URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def session(engine):
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.mark.asyncio
async def test_normalise_pipeline(session):
    # Important: We need to make sure Route uses OUR session
    route = Route(session)

    # 1. Prepare unnormalized mock data
    mock_data = {
        'site': "  INDEED  ",
        'job_title': "  SENIOR python DEVELOPER  ",
        'job_ref': "REF-pytest-integration-v2",
        'company': {
            'name': "  GLOBAL   tech  CORP  ",
            'ref': "CORP-pytest-002"
        },
        'location': "paris, france",
        'job_type': "Full   Time",
        'job_description': "Exciting opportunity for Python developers! Join us at Global Tech Corp.",
        'salaire': 85000.0,
        'platform_description': "Job search engine",
        'company_description': "A global technology company",
        'apply_description': "Direct application via portal"
    }

    # Run the pipeline
    entities = await route.normalise_pipeline(mock_data)
    
    # Assertions on returned entities
    assert "source_platform" in entities
    assert "entreprise" in entities
    assert "apply_methode" in entities
    assert "job" in entities

    # 2. Verify results in the database
    # Check SourcePlatform
    res_sp = await session.execute(select(SourcePlatform).where(SourcePlatform.name == "indeed"))
    sp = res_sp.scalar_one_or_none()
    assert sp is not None
    assert sp.name == "indeed"

    # Check Entreprise
    res_ent = await session.execute(select(Entreprise).where(Entreprise.id == "CORP-pytest-002"))
    ent = res_ent.scalar_one_or_none()
    assert ent is not None
    assert ent.name == "global tech corp"

    # Check ApplyMethode
    res_am = await session.execute(select(ApplyMethode).where(ApplyMethode.name == "full time"))
    am = res_am.scalar_one_or_none()
    assert am is not None
    assert am.name == "full time"

    # Check Job
    res_job = await session.execute(select(Job).where(Job.hash_id == "REF-pytest-integration-v2"))
    job = res_job.scalar_one_or_none()
    assert job is not None
    assert job.profile == "senior python developer"
