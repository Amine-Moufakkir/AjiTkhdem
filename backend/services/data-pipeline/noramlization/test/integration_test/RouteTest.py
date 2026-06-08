
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add src to path to allow imports from core, services, etc.
sys.path.append(os.path.join(os.getcwd(), 'src'))

from core.Route import Route
from models.base import Base, Entreprise, Job, SourcePlatform, ApplyMethode
from sqlalchemy import select

async def run_test():
    # Load environment variables
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in .env")
        return

    # Create async engine and session factory
    engine = create_async_engine(database_url, echo=False)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Ensure tables exist
    async with engine.begin() as conn:
        print("Dropping existing tables for a clean test...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        route = Route(session)

        # 1. Prepare unnormalized mock data
        # Note: The input structure matches the prompt requirements
        mock_data = {
            'site': "  INDEED  ",
            'job_title': "  SENIOR python DEVELOPER  ",
            'job_ref': "REF-999-B",
            'company': {
                'name': "  GLOBAL   tech  CORP  ",
                'ref': "CORP-001"
            },
            'location': "paris, france",
            'job_type': "Full   Time",
            'job_description': "Exciting   opportunity for Python developers!   Join us at Global Tech Corp.",
            'salaire': 75000.0,
            'platform_description': "Job search engine",
            'company_description': "A global technology company",
            'apply_description': "Direct application via portal"
        }

        print("\n=== [INPUT DATA] ===")
        for k, v in mock_data.items():
            print(f"{k}: {v}")

        print("\n=== [EXECUTING PIPELINE] ===")
        try:
            # Run the pipeline
            entities = await route.normalise_pipeline(mock_data)
            
            print("\n=== [ENTITIES EXTRACTED] ===")
            for key, entity in entities.items():
                print(f"Table: {key} -> Entity: {entity}")

            # 2. Verify results in the database
            print("\n=== [VERIFYING DATABASE PERSISTENCE] ===")
            
            # Check SourcePlatform
            # Normalization makes "  INDEED  " -> "indeed"
            res_sp = await session.execute(select(SourcePlatform).where(SourcePlatform.name == "indeed"))
            sp = res_sp.scalar_one_or_none()
            print(f"SourcePlatform: {'✅ found' if sp else '❌ NOT FOUND'} (name: {sp.name if sp else 'N/A'})")

            # Check Entreprise
            # Normalization makes "  GLOBAL   tech  CORP  " -> "global tech corp"
            res_ent = await session.execute(select(Entreprise).where(Entreprise.id == "CORP-001"))
            ent = res_ent.scalar_one_or_none()
            print(f"Entreprise:     {'✅ found' if ent else '❌ NOT FOUND'} (name: {ent.name if ent else 'N/A'}, id: {ent.id if ent else 'N/A'})")

            # Check ApplyMethode
            # Normalization makes "Full   Time" -> "full time"
            res_am = await session.execute(select(ApplyMethode).where(ApplyMethode.name == "full time"))
            am = res_am.scalar_one_or_none()
            print(f"ApplyMethode:   {'✅ found' if am else '❌ NOT FOUND'} (name: {am.name if am else 'N/A'})")

            # Check Job
            # Normalization makes "REF-999-B" -> "REF-999-B" (protected key)
            res_job = await session.execute(select(Job).where(Job.hash_id == "REF-999-B"))
            job = res_job.scalar_one_or_none()
            print(f"Job:            {'✅ found' if job else '❌ NOT FOUND'} (hash_id: {job.hash_id if job else 'N/A'}, profile: {job.profile if job else 'N/A'})")

            if sp and ent and am and job:
                print("\n✨ SUCCESS: Normalization pipeline verified. All data persisted correctly.")
            else:
                print("\n⚠️  FAILURE: Some entities were not persisted as expected.")

        except Exception as e:
            print(f"\n❌ ERROR during test execution: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_test())
