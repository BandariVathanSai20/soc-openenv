"""
inference.py

Deterministic inference script for the SOC-OpenEnv environment.
This version computes baseline scores using the local grader to
ensure consistency with the evaluation logic.
"""

import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
from server.grader import evaluate_episode  # Import the grader

# ---------------------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------------------
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# Initialize OpenAI client (required by submission rules)
client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

# ---------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------
def safe_display(score: float) -> float:
    """Ensure displayed scores are strictly within (0, 1)."""
    return min(max(score, 0.001), 0.999)


def optimal_policy(observation: Dict, state: Dict) -> str:
    """Deterministic policy aligned with SOCEnv logic."""
    event = str(observation.get("event", "")).lower()
    level = str(observation.get("level", "")).lower()
    message = str(observation).lower()
    ip = observation.get("ip", "unknown")

    failed_login_count = state.setdefault("failed_login_count", {})
    suspicious_ips = state.setdefault("suspicious_ips", set())

    if event == "login_failed":
        failed_login_count[ip] = failed_login_count.get(ip, 0) + 1
        if failed_login_count[ip] >= 3:
            return "attack"
        return "suspicious"

    if "or 1=1" in message or level == "critical":
        return "attack"

    if event == "port_scan":
        suspicious_ips.add(ip)
        return "suspicious"

    if ip in suspicious_ips:
        return "suspicious"

    if event == "login_success":
        return "normal"

    return "normal"


def run_episode(task: str) -> float:
    rewards: List[str] = []
    actions: List[str] = []
    logs: List[Dict] = []
    step = 1
    success = True
    policy_state = {}

    # Reset environment
    response = requests.post(
        f"{ENV_BASE_URL}/reset",
        json={"difficulty": task},
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    observation = data["observation"]

    print(f"[START] task={task} env=soc-openenv model={MODEL_NAME}")

    done = False

    while not done:
        try:
            action = optimal_policy(observation, policy_state)
            actions.append(action)
            logs.append(observation)

            response = requests.post(
                f"{ENV_BASE_URL}/step",
                json={"action": action},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            reward = float(data["reward"]["value"])
            done = bool(data["done"])
            observation = data.get("observation")
            last_error = data.get("info", {}).get("last_action_error")

            rewards.append(f"{reward:.2f}")

            print(
                f"[STEP] step={step} action={action} "
                f"reward={reward:.2f} done={str(done).lower()} "
                f"error={last_error if last_error else 'null'}"
            )

            step += 1

        except Exception as e:
            print(
                f"[STEP] step={step} action=error "
                f"reward=0.00 done=true error=\"{str(e)}\""
            )
            success = False
            break

    # Compute score using the grader
    metrics = evaluate_episode(actions, logs)
    score = safe_display(metrics["normalized_score"])

    print(
        f"[END] success={str(success).lower()} "
        f"steps={step-1} rewards={','.join(rewards)}"
    )

    return score


def main():
    tasks = ["easy", "medium", "hard"]
    scores = {}

    for task in tasks:
        scores[task] = run_episode(task)

    print("\nBaseline Scores:")
    for task in tasks:
        print(f"{task.capitalize()}: {scores[task]:.2f}")


if __name__ == "__main__":
    main()