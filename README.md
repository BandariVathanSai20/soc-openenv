---

title: "SOC OpenEnv"
emoji: "🛡️"
colorFrom: "blue"
colorTo: "green"
sdk: "docker"
app_port: 7860

---

# 🛡️ SOC-OpenEnv

**Deterministic Cyber Attack Simulation Environment with Hybrid LLM + Rule-Based Detection**

---

## 🔴 Live API

 https://zorooo20-soc-openenv.hf.space/docs

---

## Overview

SOC-OpenEnv is a **deterministic, step-based cybersecurity simulation environment** designed to evaluate AI/LLM agents in realistic Security Operations Center (SOC) scenarios.

Unlike static benchmarks, this system enables:

* **Sequential decision-making**
* **Context-aware attack detection**
* **Reproducible evaluation of AI agents**

---

## Key Innovation

>  **Deterministic + LLM Hybrid Architecture**

Traditional LLM-based systems are **non-deterministic and unstable**.

We solve this by combining:

* **LLM reasoning** → flexibility & generalization
* **Deterministic rules** → stability & reproducibility

Result:

* Consistent outputs across runs
* High accuracy (~0.95 score)
* Reliable evaluation system

---

## Core Features

* 🔁 **Fully deterministic environment**
* 🧩 **Step-based interaction** via `/reset`, `/step`, `/state`
* 🧠 **LLM-powered decision making (OpenAI client)**
* 🎯 **Grader-based scoring (0–1)**
* 🔥 **Multi-stage cyber attack simulation**
* 🐳 **Dockerized deployment (Hugging Face Spaces)**
* 🛡️ **Hybrid detection system (rule + AI)**

---

## OpenEnv Compliance

* ✔ Typed models (Action, Observation, State, Reward)
* ✔ Standard endpoints: `POST /reset`, `POST /step`, `GET /state`
* ✔ Deterministic grading (0.0 → 1.0)
* ✔ Multi-mode deployment ready
* ✔ `pyproject.toml`, `uv.lock`, `server/app.py` included

---

## Attack Scenarios

| Difficulty | Scenario                                                        |
| ---------- | --------------------------------------------------------------- |
| Easy       | Brute-force login detection                                     |
| Medium     | SQL injection detection                                         |
| Hard       | Multi-stage attack (recon → brute-force → exploit → escalation) |

---

## API Design

### `POST /reset`

Initializes environment

### `POST /step`

Returns:

* `current_observation`
* `next_observation`
* `reward`
* `done`
* `state`

### `GET /state`

Returns full environment state

---

## Environment Flow

```
Agent → API → SOC Environment → Logs → Detection → Reward → Agent
```

---

## Action & Observation Spaces

### Observation Space

Each observation contains structured SOC log data:

- `timestamp` (string): Event time  
- `event` (string): Type of event (e.g., login_failed, file_access)  
- `ip` (string): Source IP address  
- `query` (string): Payload or query (if any)  
- `file` (string): Target file (if any)  
- `level` (string): Severity level (INFO, WARN, CRITICAL)  

---

### Action Space

The agent must choose one of:

- `normal` → benign activity  
- `suspicious` → potential threat  
- `attack` → confirmed malicious activity  

---

## Evaluation System

* Deterministic grader
* Score range: **0.0 → 1.0**

Evaluates:

* Detection accuracy
* Sequential reasoning
* Early attack detection
* False positives / missed attacks

---

## Inference System

* Uses **OpenAI client (MANDATORY)**
* Strict logging format:

```
[START]
[STEP]
[END]
```

* Fully reproducible outputs
* Runtime < 20 minutes
* Works on low compute (2 vCPU / 8GB)

---

## ▶How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run inference

```bash
python inference.py
```

### 3. Run API locally (optional)

```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

---

## Environment Variables

The following variables must be set:

* API_BASE_URL → LLM API endpoint
* MODEL_NAME → Model identifier
* HF_TOKEN → Hugging Face API key

Example:

```bash
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export HF_TOKEN=your_token_here
```

---

## Reproducible Results

### Sample Run Output

```
[START] task=easy env=soc-openenv model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=suspicious reward=0.90 done=false error=null
[STEP] step=2 action=suspicious reward=0.30 done=false error=null
...
[END] success=true steps=5 score=0.90

[START] task=medium ...
[END] success=true score=1.00

[START] task=hard ...
[END] success=true score=0.94
```

---

## Final Scores

| Task   | Score |
| ------ | ----- |
| Easy   | 0.89  |
| Medium | 0.99  |
| Hard   | 0.94  |

**Overall Score: ~0.94–0.95**
Note: Scores are strictly bounded within (0, 1) to comply with OpenEnv evaluation constraints.

---

## What This Project Demonstrates

* Realistic **SOC workflow simulation**
* **Sequential decision-making under cyber attacks**
* Hybrid AI system (LLM + deterministic rules)
* Stable and reproducible evaluation

---

## Tech Stack

* FastAPI
* Python
* OpenAI API
* Docker
* Hugging Face Spaces

---

## Key Properties

* ✔ Fully deterministic environment
* ✔ Stable outputs across runs
* ✔ No randomness during evaluation
* ✔ No hardcoded secrets (env-based config)
* ✔ OpenEnv compliant
* ✔ Multi-mode deployment ready

---

## Use Cases

* LLM cybersecurity benchmarking
* Autonomous SOC agents
* Cyber defense simulations
* Red-team / Blue-team evaluation
* AI safety & robustness testing

---

## Conclusion

SOC-OpenEnv bridges the gap between:

**Static benchmarks ❌**
**Real-world cybersecurity systems ✅**

By combining **deterministic simulation + LLM reasoning**, it enables:

* Reliable evaluation
* Realistic attack modeling
* Stable AI decision-making

---

## Final Note

> “We solved LLM instability in SOC systems by combining deterministic rules with AI reasoning, ensuring both accuracy and reproducibility.”

---
