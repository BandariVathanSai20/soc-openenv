"""
server/models.py

Pydantic models for the SOC-OpenEnv environment.
These models define the typed schemas for actions, observations,
rewards, environment state, and API responses, ensuring compliance
with the OpenEnv specification.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime


# Action Model
class Action(BaseModel):
    """
    Represents the agent's classification of a SOC log event.
    """
    action: Literal["normal", "suspicious", "attack"] = Field(
        ...,
        description="Classification of the observed event."
    )


# Observation Model
class Observation(BaseModel):
    """
    Represents a single SOC log entry presented to the agent.
    """
    event: str = Field(..., description="Type of log event (e.g., login_failed, port_scan).")
    timestamp: Optional[datetime] = Field(
        None,
        description="Timestamp of the log entry in ISO 8601 format."
    )
    ip: Optional[str] = Field(
        None,
        description="Source IP address associated with the event."
    )
    query: Optional[str] = Field(
        None,
        description="SQL query associated with the event, if any."
    )
    file: Optional[str] = Field(
        None,
        description="File accessed during the event."
    )
    level: Optional[Literal["INFO", "WARNING", "CRITICAL"]] = Field(
        None,
        description="Severity level of the event."
    )
    step: int = Field(
        ...,
        ge=0,
        description="Current step number in the episode."
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        ...,
        description="Difficulty level of the current task."
    )


# Reward Model
class Reward(BaseModel):
    """
    Represents the reward returned after each environment step.
    """
    value: float = Field(
        ...,
        ge=-2.0,
        le=1.5,
        description="Reward value for the agent's action."
    )


# State Model
class State(BaseModel):
    """
    Represents the internal state of the environment.
    """
    step: int = Field(..., ge=0, description="Current step index.")
    history_length: int = Field(..., ge=0, description="Number of processed log entries.")
    suspicious_ips: List[str] = Field(
        default_factory=list,
        description="List of IP addresses flagged as suspicious."
    )
    failed_login_attempts: Dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of IP addresses to their failed login counts."
    )
    attack_detected: bool = Field(
        ...,
        description="Indicates whether an attack has been detected."
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        ...,
        description="Difficulty level of the current episode."
    )
    total_reward: float = Field(
        ...,
        description="Cumulative reward accumulated during the episode."
    )
    normalized_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized score between 0.0 and 1.0."
    )


# Info Model
class Info(BaseModel):
    """
    Additional information returned after each step.
    """
    attack_type: str = Field(
        ...,
        description="Type of attack detected (e.g., Brute Force, SQL Injection)."
    )
    actual_label: Literal["normal", "suspicious", "attack"] = Field(
        ...,
        description="Ground truth classification of the event."
    )
    total_reward: float = Field(
        ...,
        description="Updated cumulative reward after the step."
    )
    normalized_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized performance score."
    )


# Step Response Model
class StepResponse(BaseModel):
    """
    Response returned after each environment step.
    """
    observation: Optional[Observation] = Field(
        None,
        description="Next observation; None if the episode has ended."
    )
    reward: Reward = Field(
        ...,
        description="Reward received for the action."
    )
    done: bool = Field(
        ...,
        description="Indicates whether the episode has terminated."
    )
    state: State = Field(
        ...,
        description="Current internal state of the environment."
    )
    info: Info = Field(
        ...,
        description="Additional diagnostic information."
    )
    explanation: str = Field(
        ...,
        description="Human-readable explanation of the reward and classification."
    )


# Reset Response Model
class ResetResponse(BaseModel):
    """
    Response returned when the environment is reset.
    """
    observation: Observation = Field(
        ...,
        description="Initial observation after reset."
    )
    state: State = Field(
        ...,
        description="Initial environment state."
    )
    message: str = Field(
        ...,
        description="Confirmation message indicating successful reset."
    )