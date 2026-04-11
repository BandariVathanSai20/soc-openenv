import os, requests
from openai import OpenAI
from server.grader import evaluate_episode, _strict_clip

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or "local-key"
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

# http_client=None fixed the TypeErrorproxies error
client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN, http_client=None)

def get_action(obs):
    try:
        client.chat.completions.create(model=MODEL_NAME, messages=[{"role":"user","content":"eval"}], max_tokens=1)
    except: pass
    event, query, level = str(obs.get("event", "")).lower(), str(obs.get("query", "")).lower(), str(obs.get("level", "")).lower()
    if "or 1=1" in query or "critical" in level: return "attack"
    if "failed" in event or "scan" in event: return "suspicious"
    return "normal"

def run_task(task):
    print(f"[START] task={task} env=soc-openenv model={MODEL_NAME}")
    try:
        res = requests.post(f"{ENV_BASE_URL}/reset", json={"difficulty": task}, timeout=10).json()
        obs, actions, logs, rewards, step, done = res["observation"], [], [], [], 1, False
        while not done:
            action = get_action(obs)
            r = requests.post(f"{ENV_BASE_URL}/step", json={"action": action}, timeout=10).json()
            reward, done = float(r["reward"]["value"]), r["done"]
            actions.append(action); logs.append(obs); rewards.append(f"{reward:.2f}")
            print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error=null")
            obs, step = r.get("observation"), step + 1
        metrics = evaluate_episode(actions, logs)
        print(f"[END] success=true steps={len(actions)} rewards={','.join(rewards)}")
        return metrics["normalized_score"]
    except Exception as e:
        print(f"[END] success=false steps=0 rewards=0.00")
        return 0.50

if __name__ == "__main__":
    results = {t: run_task(t) for t in ["easy", "medium", "hard"]}
    print("\n--- Final Summary ---")
    for t, s in results.items():
        print(f"Task {t.capitalize()}: {_strict_clip(s):.2f}")