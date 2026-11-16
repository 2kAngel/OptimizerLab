"""
Modelos ORM de SQLAlchemy para DesignLab.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Integer,
    Float,
    ForeignKey,
    JSON,
    Enum,
)
from sqlalchemy.orm import relationship
from backend.database.session import Base
import enum


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    FAILED_ORPHANED = "FAILED_ORPHANED"


class ExperimentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    experiments = relationship("Experiment", back_populates="project", cascade="all, delete-orphan")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    module_id = Column(String(100), nullable=False)
    family_id = Column(String(100), nullable=False)
    status = Column(String(50), default=ExperimentStatus.DRAFT.value, nullable=False)
    configuration = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    project = relationship("Project", back_populates="experiments")
    jobs = relationship("Job", back_populates="experiment", cascade="all, delete-orphan")
    candidates = relationship("Candidate", back_populates="experiment", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(36), ForeignKey("experiments.id"), nullable=False)
    task_type = Column(String(100), nullable=False)
    status = Column(String(50), default=JobStatus.PENDING.value, nullable=False)
    payload = Column(JSON, default=dict, nullable=False)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    heartbeat_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    experiment = relationship("Experiment", back_populates="jobs")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(36), ForeignKey("experiments.id"), nullable=False)
    generation_index = Column(Integer, default=0, nullable=False)
    candidate_index = Column(Integer, default=0, nullable=False)
    parameters = Column(JSON, default=dict, nullable=False)
    geometry_hash = Column(String(64), nullable=True)
    validation_status = Column(String(50), default="VALID", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    experiment = relationship("Experiment", back_populates="candidates")
    evaluations = relationship("Evaluation", back_populates="candidate", cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    fidelity_level = Column(String(50), nullable=False)  # LEVEL_1_ANALYTICAL, LEVEL_2_CFD, etc.
    solver_name = Column(String(100), nullable=False)
    convergence_status = Column(String(50), default="CONVERGED", nullable=False)
    metrics = Column(JSON, default=dict, nullable=False)
    execution_time_seconds = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    candidate = relationship("Candidate", back_populates="evaluations")
