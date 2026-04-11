"""
server/models.py

Pydantic models for request and response schemas used by the
SOC-OpenEnv FastAPI application.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------
# Action Model
# ---------------------------------------------------------------------
class Action(BaseModel):
    """
    Represents the agent's action sent to the /step endpoint.
    Allowed values typically include: 'normal', 'suspicious', 'attack'.
    """
    action: str = Field(..., description="Agent action")


# ---------------------------------------------------------------------
# Observation Model
# ---------------------------------------------------------------------
class Observation(BaseModel):
    """
    Represents an observation returned by the environment.
    """
    step: int
    event: str
    ip: str
    level: str
    difficulty: Optional[str] = None


# ---------------------------------------------------------------------
# State Model
# ---------------------------------------------------------------------
class State(BaseModel):
    """
    Represents the internal state of the environment.
    """
    step: int
    total_reward: float
    difficulty: str


# ---------------------------------------------------------------------
# Reward Model
# ---------------------------------------------------------------------
class Reward(BaseModel):
    """
    Represents the reward returned after each step.
    """
    value: float


# ---------------------------------------------------------------------
# Info Model
# ---------------------------------------------------------------------
class Info(BaseModel):
    """
    Additional metadata returned by the environment.
    Includes grader metrics required by the OpenEnv validator.
    """

    # Environment details
    actual_label: Optional[str] = None
    attack_type: Optional[str] = None
    last_action_error: Optional[str] = None

    # Grader metrics (must be strictly within (0, 1))
    normalized_score: Optional[float] = Field(
        default=0.5, gt=0.0, lt=1.0
    )
    accuracy: Optional[float] = Field(
        default=0.5, gt=0.0, lt=1.0
    )
    false_positive_rate: Optional[float] = Field(
        default=0.5, gt=0.0, lt=1.0
    )
    missed_attack_rate: Optional[float] = Field(
        default=0.5, gt=0.0, lt=1.0
    )
    early_detection_bonus: Optional[float] = Field(
        default=0.5, gt=0.0, lt=1.0
    )

    class Config:
        extra = "allow"  # Allows additional fields if present


# ---------------------------------------------------------------------
# Step Response Model
# ---------------------------------------------------------------------
class StepResponse(BaseModel):
    """
    Response schema for the /step endpoint.
    """
    observation: Optional[Observation]
    reward: Reward
    done: bool
    state: State
    info: Info
    explanation: str


# ---------------------------------------------------------------------
# Reset Response Model
# ---------------------------------------------------------------------
class ResetResponse(BaseModel):
    """
    Response schema for the /reset endpoint.
    """
    observation: Observation
    state: State
    message: str