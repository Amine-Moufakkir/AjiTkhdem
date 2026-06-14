from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class JobCleanedDTO:
    """
    DTO représentant une offre d'emploi extraite et parsée.
    """
    site: Optional[str] = None
    job_title: Optional[str] = None
    job_ref: Optional[str] = None
    company: Dict[str, Optional[str]] = field(default_factory=lambda: {"name": None, "ref": None})
    location: Optional[str] = None
    job_type: Optional[str] = None
    job_description: Optional[str] = None
    url: Optional[str] = None
    hash: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return asdict(self)
