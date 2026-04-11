import os
import uvicorn
from fastapi import FastAPI, Body, HTTPException
from server.environment import SOCEnv
from server.models import Action, StepResponse, ResetResponse, Info, Reward, State, Observation
from server.grader import evaluate_episode, _strict_clip

app = FastAPI(title="SOC-OpenEnv Server")
env = SOCEnv()

@app.get("/")
def home():
    """Root endpoint to show the API is alive and prevent 404."""
    return {
        "message": "SOC-OpenEnv API is running",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset", response_model=ResetResponse)
def reset(data: dict = Body(None)):
    diff = data.get("difficulty", "easy") if data else "easy"
    env.difficulty = diff
    obs = env.reset()
    return ResetResponse(
        observation=Observation(**obs), 
        state=State(**env.state()), 
        message="OK"
    )

@app.post("/step", response_model=StepResponse)
def step(req: Action):
    try:
        logs_subset = env.logs[:env.current_step + 1]
        next_obs, reward, done, info_dict = env.step(req.action)
        if done:
            metrics = evaluate_episode(env.actions, logs_subset)
        else:
            metrics = {k: 0.45 for k in ["normalized_score", "accuracy", "false_positive_rate", "missed_attack_rate", "early_detection_bonus"]}

        return StepResponse(
            observation=Observation(**next_obs) if next_obs else None,
            reward=Reward(value=reward),
            done=done,
            state=State(**env.state()),
            info=Info(
                actual_label=info_dict["actual_label"], 
                attack_type=info_dict["attack_type"], 
                **metrics
            ),
            explanation="Step processed"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state", response_model=State)
def get_state():
    return State(**env.state())

def main():
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()