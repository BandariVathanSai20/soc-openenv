"""
server/models.py

Pydantic models for SOC-OpenEnv FastAPI application.
"""

from pydantic import BaseModel, Field
from typing import Optional


class Action(BaseModel):
    """Agent action sent to the /step endpoint."""
    action: str = Field(..., description="Agent action: normal, suspicious, or attack")


class Observation(BaseModel):
    """Observation returned by the environment."""
    step: int
    event: str
    ip: str
    level: str
    difficulty: str


class State(BaseModel):
    """Internal environment state."""
    step: int
    total_reward: float
    difficulty: str


class Reward(BaseModel):
    """Reward returned after each step."""
    value: float


class Info(BaseModel):
    """Additional metadata including grader metrics."""
    actual_label: Optional[str] = None
    attack_type: Optional[str] = None
    last_action_error: Optional[str] = None

    # Metrics must be strictly within (0,1)
    normalized_score: float = Field(default=0.5, gt=0.0, lt=1.0)
    accuracy: float = Field(default=0.5, gt=0.0, lt=1.0)
    false_positive_rate: float = Field(default=0.5, gt=0.0, lt=1.0)
    missed_attack_rate: float = Field(default=0.5, gt=0.0, lt=1.0)
    early_detection_bonus: float = Field(default=0.5, gt=0.0, lt=1.0)

    class Config:
        extra = "allow"


class StepResponse(BaseModel):
    """Response for /step endpoint."""
    observation: Optional[Observation]
    reward: Reward
    done: bool
    state: State
    info: Info
    explanation: str


class ResetResponse(BaseModel):
    """Response for /reset endpoint."""
    observation: Observation
    state: State
    message: str