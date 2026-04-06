import os
import requests
from openai import OpenAI
from env.grader import evaluate_episode
from dotenv import load_dotenv

load_dotenv()

# ENV VARIABLES
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

# ENV API (my SOC environment)
ENV_BASE_URL = "https://zorooo20-soc-openenv.hf.space"

# OpenAI client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

# LOGGING
def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done, error=None):
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# LLM PROMPT
SYSTEM_PROMPT = """
You are a cybersecurity SOC analyst.

Classify the log into exactly one:
normal
suspicious
attack

Rules:
- Multiple login_failed → suspicious → attack if repeated
- 'OR 1=1' → attack
- CRITICAL → attack
- port_scan → suspicious
- Otherwise → normal

Respond ONLY with one word.
"""


# HYBRID AGENT
def decide_action(observation):
    obs_str = str(observation)

    # --------- ALWAYS CALL LLM ---------
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": obs_str}
            ],
            temperature=0,
            max_tokens=5
        )

        llm_action = response.choices[0].message.content.strip().lower()

        if llm_action not in ["normal", "suspicious", "attack"]:
            llm_action = "normal"

    except Exception:
        llm_action = "normal"

    # --------- RULE OVERRIDE ---------

    if "OR 1=1" in obs_str:
        return "attack"

    if "CRITICAL" in obs_str:
        return "attack"

    if "port_scan" in obs_str:
        return "suspicious"

    if "login_failed" in obs_str:
        return "suspicious"

    return llm_action


# RUN TASK
def run_task(difficulty):
    rewards = []
    steps = 0

    actions = []
    logs = []

    log_start(task=difficulty, env="soc-openenv", model=MODEL_NAME)

    res = requests.post(
        f"{ENV_BASE_URL}/reset",
        json={"difficulty": difficulty}
    )

    if res.status_code != 200:
        raise Exception(f"/reset failed: {res.text}")

    data = res.json()

    if "observation" not in data:
        raise Exception(f"Invalid reset response: {data}")

    observation = data["observation"]
    done = False

    while not done:
        action = decide_action(observation)

        actions.append(action)
        logs.append(observation)

        res = requests.post(
            f"{ENV_BASE_URL}/step",
            json={"action": action}
        )

        if res.status_code != 200:
            raise Exception(f"/step failed: {res.text}")

        result = res.json()

        reward = result["reward"]["value"]
        done = result["done"]

        rewards.append(reward)
        steps += 1

        log_step(
            step=steps,
            action=action,
            reward=reward,
            done=done,
            error=None
        )

        observation = result.get("next_observation")

    score = evaluate_episode(actions, logs)
    success = score >= 0.5

    log_end(
        success=success,
        steps=steps,
        score=score,
        rewards=rewards
    )

    return score


# MAIN
def main():
    tasks = ["easy", "medium", "hard"]

    for task in tasks:
        run_task(task)


if __name__ == "__main__":
    main()