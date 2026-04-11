from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict


#  Action space 
class Action(BaseModel):
    action: Literal["normal", "suspicious", "attack"]


#  Observation 
class Observation(BaseModel):
    event: str
    timestamp: Optional[str] = None
    ip: Optional[str] = None
    query: Optional[str] = None
    file: Optional[str] = None
    level: Optional[str] = None


#  Reward model
class Reward(BaseModel):
    value: float = Field(..., ge=-5, le=5)


#  State 
class State(BaseModel):
    step: int
    history_length: int
    suspicious_ips: List[str]
    failed_login_attempts: Dict[str, int]
    attack_detected: bool
    difficulty: str 


#  Step Response 
class StepResponse(BaseModel):
    current_observation: Observation
    next_observation: Optional[Observation]
    reward: Reward
    done: bool
    state: State
    explanation: str


#  Reset Response
class ResetResponse(BaseModel):
    observation: Observation
    state: State
    message: str