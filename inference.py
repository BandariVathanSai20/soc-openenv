"""
inference.py

Baseline inference script for the SOC-OpenEnv environment.
This script interacts with the deployed environment via HTTP,
uses the OpenAI client for optional reasoning, and emits logs
in the exact format required by the OpenEnv RL Challenge.
"""

import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict
from server.grader import evaluate_episode

# Load Environment Variables
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# Initialize OpenAI Client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

# Logging Functions 
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str = "null") -> None:
    print(
        f"[STEP] step={step} action={action} "
        f"reward={reward:.2f} done={str(done).lower()} error={error}",
        flush=True,
    )


def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} "
        f"steps={steps} rewards={rewards_str}",
        flush=True,
    )

# Stateful SOC Agent
class SOCAgent:
    """
    Rule-based SOC agent with optional LLM reasoning.
    """

    def __init__(self):
        self.failed_login_count: Dict[str, int] = {}
        self.suspicious_ips = set()

    def decide(self, observation: Dict) -> str:
        if observation is None:
            return "normal"

        event = observation.get("event", "")
        level = observation.get("level", "")
        query = str(observation.get("query", "")).lower()
        ip = observation.get("ip", "")

        # SQL Injection
        if "or 1=1" in query:
            return "attack"

        # Privilege Escalation
        if level == "CRITICAL":
            return "attack"

        # Port Scan
        if event == "port_scan":
            self.suspicious_ips.add(ip)
            return "suspicious"

        # Brute Force Detection
        if event == "login_failed":
            self.failed_login_count[ip] = (
                self.failed_login_count.get(ip, 0) + 1
            )
            if self.failed_login_count[ip] >= 3:
                return "attack"
            return "suspicious"

        # Suspicious continuation
        if ip in self.suspicious_ips:
            return "suspicious"

        # Optional LLM reasoning for ambiguous cases
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Classify the following SOC log as "
                            "normal, suspicious, or attack. "
                            "Respond with only one word."
                        ),
                    },
                    {"role": "user", "content": str(observation)},
                ],
                temperature=0,
                max_tokens=5,
            )
            action = response.choices[0].message.content.strip().lower()
            if action in {"normal", "suspicious", "attack"}:
                return action
        except Exception:
            # Fallback to default behavior
            pass

        return "normal"

# Run a Single Task
def run_task(task_id: str) -> float:
    rewards: List[float] = []
    actions: List[str] = []
    logs: List[Dict] = []
    steps = 0
    success = False

    agent = SOCAgent()
    log_start(task=task_id, env="soc-openenv", model=MODEL_NAME)

    try:
        # Reset environment
        response = requests.post(
            f"{ENV_BASE_URL}/reset",
            json={"difficulty": task_id},
            timeout=30,
        )
        response.raise_for_status()
        observation = response.json().get("observation")
        done = False

        # Episode loop
        while not done:
            action = agent.decide(observation)
            actions.append(action)
            logs.append(observation)

            response = requests.post(
                f"{ENV_BASE_URL}/step",
                json={"action": action},
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()

            reward = float(result["reward"]["value"])
            done = bool(result["done"])
            observation = result.get("observation")

            rewards.append(reward)
            steps += 1

            log_step(step=steps, action=action, reward=reward, done=done)

        # Evaluate episode using deterministic grader
        metrics = evaluate_episode(actions, logs)
        normalized_score = metrics["normalized_score"]
        success = normalized_score >= 0.7  # Success threshold

    except Exception as e:
        log_step(step=steps + 1, action="error", reward=0.00, done=True, error=str(e))
        success = False

    finally:
        log_end(success=success, steps=steps, rewards=rewards)

    return normalized_score if 'normalized_score' in locals() else 0.0

# Main Execution
def main():
    """
    Run inference for all tasks: easy, medium, and hard.
    """
    tasks = ["easy", "medium", "hard"]
    scores = {}

    for task in tasks:
        score = run_task(task)
        scores[task] = score

    print("\nBaseline Scores:")
    for task, score in scores.items():
        print(f"{task.capitalize()}: {score:.2f}")


if __name__ == "__main__":
    main()