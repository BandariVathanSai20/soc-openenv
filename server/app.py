"""
server/app.py

FastAPI application exposing the SOC-OpenEnv environment.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import logging

from server.environment import SOCEnv
from server.models import (
    Action,
    Observation,
    State,
    Reward,
    StepResponse,
    ResetResponse,
    Info,
)
from server.grader import evaluate_episode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SOC OpenEnv API",
    version="1.0",
    description="AI-powered Security Operations Center simulation environment.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_DIFFICULTY = os.getenv("DEFAULT_DIFFICULTY", "easy")
env = SOCEnv(difficulty=DEFAULT_DIFFICULTY)


class ResetRequest(BaseModel):
    difficulty: Optional[str] = "easy"


@app.get("/")
def home():
    return {"message": "SOC OpenEnv API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reset", response_model=ResetResponse)
def reset(request: Optional[ResetRequest] = Body(default=None)):
    global env

    difficulty = DEFAULT_DIFFICULTY
    if request and request.difficulty:
        difficulty = request.difficulty.lower()

    if difficulty not in {"easy", "medium", "hard"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid difficulty. Choose from 'easy', 'medium', or 'hard'.",
        )

    env = SOCEnv(difficulty=difficulty)
    obs = env.reset()

    return ResetResponse(
        observation=Observation(**obs),
        state=State(**env.state()),
        message=f"Environment reset to {difficulty}",
    )


@app.post("/step", response_model=StepResponse)
def step(action: Action):
    global env

    if env.current_step >= len(env.logs):
        raise HTTPException(
            status_code=400,
            detail="Episode has finished. Please call /reset to start a new episode.",
        )

    current_obs = env.logs[env.current_step]
    actual_label, attack_type = env.detect_attack(current_obs)

    next_obs, reward, done, info = env.step(action.action)

    if info is None:
        info = {}

    if done:
        metrics = evaluate_episode(env.actions, env.logs)
        info.update(metrics)
    else:
        info.update({
            "normalized_score": 0.5,
            "accuracy": 0.5,
            "false_positive_rate": 0.5,
            "missed_attack_rate": 0.5,
            "early_detection_bonus": 0.5,
        })

    explanation = (
        f"Agent chose '{action.action}' vs actual '{actual_label}' "
        f"({attack_type}). Reward: {reward}."
    )

    return StepResponse(
        observation=Observation(**next_obs) if next_obs else None,
        reward=Reward(value=float(reward)),
        done=bool(done),
        state=State(**env.state()),
        info=Info(**info),
        explanation=explanation,
    )


@app.get("/state", response_model=State)
def get_state():
    return State(**env.state())


def main():
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()