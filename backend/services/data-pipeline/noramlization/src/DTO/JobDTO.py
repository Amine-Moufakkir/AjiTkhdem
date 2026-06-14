from pydantic import BaseModel
from typing import List, Optional, Dict

class RecommendationRequest(BaseModel):
    profiles: List[str]

class MatchReasons(BaseModel):
    skills: str
    location: str
    salary: str
    jobType: str

class MatchInfo(BaseModel):
    jobId: Optional[str] = None
    score: int
    reasons: Optional[MatchReasons] = None

class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: str
    workModel: Optional[str] = "Hybrid"
    salaryMin: Optional[float] = None
    salaryMax: Optional[float] = None
    type: str
    description: str
    requirements: List[str] = []
    match: MatchInfo
    applied: bool = False
    applicationStatus: Optional[str] = None

class JobListResponse(BaseModel):
    jobs: List[JobResponse]
