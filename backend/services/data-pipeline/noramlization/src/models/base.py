from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Text, DateTime, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class JobStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"

class Entreprise(Base):
    __tablename__ = "entreprise"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relations
    jobs: Mapped[List["Job"]] = relationship(back_populates="entreprise")
    employes: Mapped[List["Employe"]] = relationship(back_populates="entreprise")

class Job(Base):
    __tablename__ = "job"

    hash_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    description: Mapped[str] = mapped_column(Text)
    profile: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    date_creation: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[JobStatus] = mapped_column(default=JobStatus.OPEN)
    salaire: Mapped[Optional[float]] = mapped_column(Float)

    # Foreign Keys
    entreprise_id: Mapped[int] = mapped_column(ForeignKey("entreprise.id"))
    source_platform_id: Mapped[int] = mapped_column(ForeignKey("source_platform.id"))
    apply_methode_id: Mapped[int] = mapped_column(ForeignKey("apply_methode.id"))

    # Relations
    entreprise: Mapped["Entreprise"] = relationship(back_populates="jobs")
    source_platform: Mapped["SourcePlatform"] = relationship(back_populates="jobs")
    apply_methode: Mapped["ApplyMethode"] = relationship(back_populates="jobs")

class Employe(Base):
    __tablename__ = "employe"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    social_media: Mapped[Optional[str]] = mapped_column(String(255))

    entreprise_id: Mapped[Optional[int]] = mapped_column(ForeignKey("entreprise.id"))
    entreprise: Mapped["Entreprise"] = relationship(back_populates="employes")

class SourcePlatform(Base):
    __tablename__ = "source_platform"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    jobs: Mapped[List["Job"]] = relationship(back_populates="source_platform")

class ApplyMethode(Base):
    __tablename__ = "apply_methode"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    jobs: Mapped[List["Job"]] = relationship(back_populates="apply_methode")