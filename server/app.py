import os
import uvicorn
from fastapi import FastAPI, Body, HTTPException
from server.environment import SOCEnv
from server.models import Action, StepResponse, ResetResponse, Info, Reward, State, Observation
from server.grader import evaluate_episode

app = FastAPI(title="SOC-OpenEnv Server")
env = SOCEnv()

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
        # Reference logs for grading before step increment
        logs_subset = env.logs[:env.current_step + 1]
        
        next_obs, reward, done, info_dict = env.step(req.action)
        
        metrics = evaluate_episode(env.actions, logs_subset) if done else {
            "normalized_score": 0.5, "accuracy": 0.5, "false_positive_rate": 0.5, 
            "missed_attack_rate": 0.5, "early_detection_bonus": 0.5
        }

        return StepResponse(
            observation=Observation(**next_obs) if next_obs else None,
            reward=Reward(value=reward),
            done=done,
            state=State(**env.state()),
            info=Info(actual_label=info_dict["actual_label"], **metrics),
            explanation="Step processed"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def get_state():
    return env.state()

def main():
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port, log_level="error")

if __name__ == "__main__":
    main()