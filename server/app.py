from fastapi import FastAPI, HTTPException
import uvicorn

from env.environment import SOCEnv
from env.models import Action, Observation, State, Reward, StepResponse, ResetResponse

app = FastAPI(title="SOC OpenEnv API", version="1.0")

env = SOCEnv(difficulty="easy")


@app.post("/reset", response_model=ResetResponse)
def reset(payload: dict = {}):
    global env

    difficulty = payload.get("difficulty", "easy")

    if difficulty not in ["easy", "medium", "hard"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty")

    env = SOCEnv(difficulty=difficulty)
    obs = env.reset()

    return {
        "observation": Observation(**obs),
        "state": State(**env.state()),
        "message": f"Environment reset to {difficulty}"
    }


@app.post("/step", response_model=StepResponse)
def step(action: Action):
    global env

    current_obs = env.logs[env.current_step]
    actual, attack_type = env.detect_attack(current_obs)

    obs, reward, done, _ = env.step(action.action)

    explanation = f"Agent chose '{action.action}' vs actual '{actual}' ({attack_type})"

    return {
        "current_observation": Observation(**current_obs),
        "next_observation": Observation(**obs) if obs else None,
        "reward": Reward(value=reward),
        "done": done,
        "state": State(**env.state()),
        "explanation": explanation
    }


@app.get("/state", response_model=State)
def get_state():
    return State(**env.state())


@app.get("/")
def home():
    return {"message": "SOC OpenEnv API running"}


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()