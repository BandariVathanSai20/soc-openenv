from pydantic import BaseModel
from typing import Optional

class Action(BaseModel):
    action: str

class Observation(BaseModel):
    step: int
    event: Optional[str] = None
    ip: Optional[str] = None
    level: Optional[str] = None
    difficulty: str
    query: Optional[str] = None
    file: Optional[str] = None

class State(BaseModel):
    step: int
    total_reward: float
    difficulty: str

class Reward(BaseModel):
    value: float

class Info(BaseModel):
    actual_label: Optional[str] = "normal"
    normalized_score: float = 0.5
    accuracy: float = 0.5
    false_positive_rate: float = 0.5
    missed_attack_rate: float = 0.5
    early_detection_bonus: float = 0.5

class StepResponse(BaseModel):
    observation: Optional[Observation]
    reward: Reward
    done: bool
    state: State
    info: Info
    explanation: str

class ResetResponse(BaseModel):
    observation: Observation
    state: State
    message: str