# server/models.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class Info(BaseModel):
    actual_label: Optional[str] = None
    attack_type: Optional[str] = None
    last_action_error: Optional[str] = None

    # Grader metrics required by the validator
    normalized_score: Optional[float] = Field(default=0.5, gt=0.0, lt=1.0)
    accuracy: Optional[float] = Field(default=0.5, gt=0.0, lt=1.0)
    false_positive_rate: Optional[float] = Field(default=0.5, gt=0.0, lt=1.0)
    missed_attack_rate: Optional[float] = Field(default=0.5, gt=0.0, lt=1.0)
    early_detection_bonus: Optional[float] = Field(default=0.5, gt=0.0, lt=1.0)

    class Config:
        extra = "allow"  # Ensures additional fields are not discarded