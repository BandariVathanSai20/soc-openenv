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

👉 https://zorooo20-soc-openenv.hf.space/docs

---

## Why This Matters

Security Operations Centers (SOCs) operate in **high-stakes, real-time environments**, where analysts must make **sequential decisions under uncertainty**.

Traditional benchmarks fail because they:

* Evaluate single-step outputs
* Ignore temporal attack patterns
* Lack real-world context

**SOC-OpenEnv solves this by enabling:**

* Multi-step reasoning
* Context-aware threat detection
* Deterministic and reproducible evaluation

---

## Overview

SOC-OpenEnv is a **deterministic, step-based cybersecurity simulation environment** designed to evaluate AI/LLM agents in realistic SOC workflows.

Unlike static datasets, this environment enables:

* **Sequential decision-making**
* **Context-aware attack detection**
* **Reproducible agent evaluation**

---

## Key Innovation

> **Deterministic + LLM Hybrid Architecture**

LLMs are powerful but **non-deterministic and inconsistent**.

We combine:

| Component           | Purpose                       |
| ------------------- | ----------------------------- |
| LLM reasoning       | Generalization & intelligence |
| Deterministic rules | Stability & reproducibility   |

### Result:

* 🔁 Consistent outputs across runs
* 🎯 High performance (~0.9+ scores)
* 🛡️ Reliable evaluation system

---

## Core Features

* 🔁 Fully deterministic environment
* 🧩 Step-based interaction (`/reset`, `/step`, `/state`)
* 🧠 LLM-powered decision making
* 🎯 Grader-based scoring (strictly between 0–1)
* 🔥 Multi-stage cyber attack simulation
* 🐳 Dockerized deployment (HF Spaces)
* 🛡️ Hybrid detection (rules + AI)

---

## Determinism Guarantee

* No randomness in environment transitions
* Fixed simulation logic
* Same input → same output
* Fully reproducible evaluation

---

## OpenEnv Compliance

* Typed models (Observation, Action, Reward, State)
* Standard endpoints (`reset`, `step`, `state`)
* Deterministic grader
* Multi-mode deployment ready

---

## Attack Scenarios

| Difficulty | Scenario                                                        |
| ---------- | --------------------------------------------------------------- |
| Easy       | Brute-force login detection                                     |
| Medium     | SQL injection detection                                         |
| Hard       | Multi-stage attack (recon → brute-force → exploit → escalation) |

---

## Action & Observation Spaces

### Observation Space

Structured SOC log:

* `timestamp` → event time
* `event` → type (login_failed, port_scan, etc.)
* `ip` → source IP
* `query` → payload
* `file` → accessed file
* `level` → severity (INFO, WARN, CRITICAL)

---

### Action Space

The agent must classify:

* `normal`
* `suspicious`
* `attack`

---

## Reward Design (Key Strength)

| Scenario                 | Reward          |
| ------------------------ | --------------- |
| Correct classification   | ~0.95           |
| Suspicious vs attack     | 0.5             |
| Incorrect classification | ~0.05           |
| Early attack detection   | +0.1 bonus      |
| Final score range        | strictly (0, 1) |

Encourages early detection
Penalizes mistakes
Provides dense learning signal

---

## Environment Flow

```
Agent → API → Environment → Logs → Detection → Reward → Agent
```

---

## API Design

### `POST /reset`

Initialize environment

### `POST /step`

Returns:

* observation
* reward
* done
* state

### `GET /state`

Returns full environment state

---

## Inference System

* Uses OpenAI client
* Structured logs:

```
[START]
[STEP]
[END]
```

* Deterministic outputs
* Low compute requirement

---

## ▶ How to Run

```bash
pip install -r requirements.txt
python inference.py
```

---

## Environment Variables

```bash
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
HF_TOKEN=your_token_here
```

---

## Baseline Results

| Task   | Score |
| ------ | ----- |
| Easy   | 0.86  |
| Medium | 0.98  |
| Hard   | 0.90  |

**Overall Score: ~0.91–0.93**

> Scores are strictly bounded within (0, 1) to comply with OpenEnv evaluation constraints.

---

## What This Project Demonstrates
* Realistic SOC workflow simulation
* Sequential decision-making under attacks
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

* Fully deterministic
* Stable outputs
* No randomness
* OpenEnv compliant
* Production-style design

---

## Use Cases

* LLM cybersecurity benchmarking
* Autonomous SOC agents
* Red-team / Blue-team evaluation
* AI safety testing

---

## Conclusion

SOC-OpenEnv bridges the gap between:

❌ Static benchmarks
✅ Real-world cybersecurity systems

By combining **deterministic simulation + LLM reasoning**, it enables:

* Reliable evaluation
* Realistic attack modeling
* Stable AI decision-making

---

## Final Note

> “We solve LLM instability in cybersecurity by combining deterministic rules with intelligent reasoning, achieving both accuracy and reproducibility.”
