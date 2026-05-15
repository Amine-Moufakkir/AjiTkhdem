from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class JobCleanedDTO:
    """
    DTO représentant une offre d'emploi extraite et parsée.
    Contient tous les champs extraits par IndeedParser et autres parsers.
    """

    def __init__(self) :
        pass
    
    site: str  | None
    job_title: str | None
    job_ref: str | None
    company: Dict[str, Optional[str]]  # {name, ref}
    location: Optional[str] | None
    job_type: Optional[str] | None
    job_description: Optional[str] | None
    url: Optional[str] = None
    hash: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return asdict(self)
    

