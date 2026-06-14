import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from config.db import AsyncSessionLocal
from models.JobCrud import JobCRUD
from DTO.JobDTO import RecommendationRequest, JobListResponse, JobResponse, MatchInfo, MatchReasons

router = APIRouter(prefix="/api")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def mock_gemini_matching(job_title: str, profile: str) -> MatchInfo:
    """Simule l'évaluation d'adéquation par l'IA Gemini."""
    score = random.randint(60, 95)
    reasons = MatchReasons(
        skills=f"Votre profil de {profile} correspond idéalement aux compétences demandées pour ce poste de {job_title}.",
        location="Le statut hybride répond parfaitement à vos critères.",
        salary="Votre attente salariale est en phase avec la grille de l'entreprise.",
        jobType="Le poste cadre avec vos projets professionnels."
    )
    return MatchInfo(score=score, reasons=reasons)

@router.post("/recommendations", response_model=JobListResponse)
async def get_recommendations(request: RecommendationRequest, db: AsyncSession = Depends(get_db)):
    job_crud = JobCRUD(db)
    # On cherche les jobs qui matchent les profils
    db_jobs = await job_crud.search_jobs(request.profiles)
    
    jobs_out = []
    for db_job in db_jobs:
        # On utilise le premier profil pour le mock ou on itère
        profile_used = request.profiles[0] if request.profiles else "Candidat"
        match_info = mock_gemini_matching(db_job.profile or db_job.description[:20], profile_used)
        match_info.jobId = db_job.hash_id
        
        jobs_out.append(JobResponse(
            id=db_job.hash_id,
            title=db_job.profile or "Poste inconnu",
            company=db_job.entreprise.name if db_job.entreprise else "Entreprise anonyme",
            location=db_job.location or "À distance",
            workModel="Hybrid",
            salaryMin=db_job.salaire,
            salaryMax=(db_job.salaire * 1.2) if db_job.salaire else None,
            type=db_job.job_type or "CDI",
            description=db_job.description,
            requirements=["Python", "SQL"], # Mocké car non présent en base
            match=match_info,
            applied=False,
            applicationStatus=None
        ))
    
    return JobListResponse(jobs=jobs_out)

@router.get("/jobs", response_model=JobListResponse)
async def get_jobs(db: AsyncSession = Depends(get_db)):
    job_crud = JobCRUD(db)
    db_jobs = await job_crud.get_all()
    
    jobs_out = []
    for db_job in db_jobs:
        # Score calculé à la volée (mocké)
        match_info = MatchInfo(score=random.randint(50, 80))
        
        jobs_out.append(JobResponse(
            id=db_job.hash_id,
            title=db_job.profile or "Poste inconnu",
            company=db_job.entreprise.name if db_job.entreprise else "Entreprise anonyme",
            location=db_job.location or "À distance",
            workModel="Hybrid",
            salaryMin=db_job.salaire,
            salaryMax=(db_job.salaire * 1.2) if db_job.salaire else None,
            type=db_job.job_type or "CDI",
            description=db_job.description,
            requirements=[],
            match=match_info,
            applied=False,
            applicationStatus=None
        ))
    
    return JobListResponse(jobs=jobs_out)
