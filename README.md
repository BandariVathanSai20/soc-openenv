---
app_port: 7860
colorFrom: blue
colorTo: green
emoji: 🛡️
sdk: docker
title: SOC OpenEnv
---

# 🛡️ SOC-OpenEnv

SOC-OpenEnv is a deterministic **Security Operations Center (SOC)** simulation environment designed to evaluate AI agents in cybersecurity decision-making tasks. It is fully compliant with the **OpenEnv** benchmark requirements for the Meta PyTorch Hackathon.

## 🚀 Overview

SOC-OpenEnv simulates realistic cybersecurity events such as brute-force login attempts, SQL injection attacks, and multi-stage **Advanced Persistent Threats (APT)**. Agents must classify each event as **normal**, **suspicious**, or **attack**.

## ✨ Key Features

- ✅ **Phase 2 Validated**: All scores are strictly within the open interval $(0, 1)$.
- 🔁 **Deterministic**: Reproducible scenarios across multiple runs.
- 🎯 **Three Difficulty Levels**: Easy (Brute Force), Medium (SQLi), and Hard (APT).
- ⚡ **FastAPI Powered**: Low-latency REST API.
- 🐳 **Docker Optimized**: Ready for deployment on Hugging Face Spaces.
- 🤖 **OpenAI Compatible**: Inference script uses standard OpenAI client signatures.

## 🧠 Environment Description

### 🔍 Observation Space
Field | Description
--- | ---
`event` | Type of event (e.g., `login_failed`, `query`, `port_scan`)
`ip` | Source IP address
`level` | Severity level (INFO, WARN, CRITICAL)
`query` | SQL query (if applicable)
`step` | Current step in the episode
`difficulty` | Scenario difficulty (easy, medium, hard)

### 🎮 Action Space
- `normal`: Benign activity.
- `suspicious`: Potentially malicious/investigative activity.
- `attack`: Confirmed malicious activity.

## 📊 Grading Scheme

The environment uses a deterministic grader that evaluates the sequence of actions against ground truth.

| Outcome | Reward (Step) | Score (Grader) |
|---------|---------------|----------------|
| Correct Match | +1.00 | Included in Accuracy |
| Incorrect Match | -1.00 | Penalty applied |

**Note on Normalization:** The final score is clipped strictly between **0.01 and 0.99** to ensure compliance with benchmark validation rules.

## 📊 Baseline Performance

Evaluated using `Qwen/Qwen2.5-72B-Instruct`. These results are deterministic.

| Difficulty | Normalized Score |
|------------|------------------|
| Easy       | 0.80             |
| Medium     | 0.85             |
| Hard       | 0.85             |

### 🧪 Example Inference Output

```text
[START] task=easy env=soc-openenv model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=suspicious reward=1.00 done=false error=null
[STEP] step=2 action=suspicious reward=1.00 done=false error=null
[STEP] step=3 action=suspicious reward=-1.00 done=false error=null
[STEP] step=4 action=normal reward=1.00 done=false error=null
[STEP] step=5 action=normal reward=1.00 done=true error=null
[END] success=true steps=5 rewards=1.00,1.00,-1.00,1.00,1.00

--- Final Summary ---
Task Easy: 0.80
Task Medium: 0.85
Task Hard: 0.85

## Reward and Evaluation Design

SOC-OpenEnv follows the architectural principles of official OpenEnv environments such as TBench2, CARLA, and REPL.

### Environment Rewards
- Returned by the `/step` endpoint.
- Provide immediate feedback to the agent.
- Include bonuses for early detection and penalties for false positives or missed attacks.
- Suitable for reinforcement learning and agent training.

### Grader Evaluation
- Implemented in `server/grader.py`.
- Computes standardized metrics such as normalized score, accuracy, false positives, and missed attacks.
- The final benchmark score is normalized to the range [0, 1] and is used for evaluation.

This separation ensures both expressive agent feedback and fair benchmarking.

## 🛠️ Installation

### 1. Clone the Repository

``` bash
git clone https://github.com/BandariVathanSai20/soc-openenv.git
cd soc-openenv
```

### 2. Create and Activate a Virtual Environment

#### Windows (PowerShell)

``` bash
python -m venv .venv
.\.venv\Scripts\activate
```

#### Linux/macOS

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

``` bash
pip install --upgrade pip
pip install -r requirements.txt
```

## ▶️ Running the Environment

``` bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Health Check

``` bash
curl http://localhost:7860/health
```

## 🤖 Running the Baseline Agent

``` bash
python inference.py
```

## 🧪 Running Tests

``` bash
python -m pytest tests/
```

**Expected Output**

``` text
==================== 12 passed ====================
```

## 🐳 Docker Deployment

### Build the Docker Image

``` bash
docker build -t soc-openenv .
```

### Run the Docker Container

``` bash
docker run -p 7860:7860 soc-openenv
```

## ✅ OpenEnv Validation

``` bash
bash scripts/validate-submission.sh http://localhost:7860
```

**Successful Output**

``` text
All 3/3 checks passed!
Your submission is ready to submit.
```

## 🌐 API Endpoints

  Endpoint    Method   Description
  ----------- -------- ------------------------
  `/health`   GET      Service health check
  `/reset`    POST     Reset environment
  `/step`     POST     Execute an action
  `/state`    GET      Retrieve current state

## 📦 Example API Usage

### Reset the Environment

``` bash
curl -X POST http://localhost:7860/reset \
     -H "Content-Type: application/json" \
     -d '{"difficulty":"easy"}'
```

### Perform a Step

``` bash
curl -X POST http://localhost:7860/step \
     -H "Content-Type: application/json" \
     -d '{"action":"suspicious"}'
```

## ☁️ Deployment to Hugging Face Spaces

1.  Create a new **Hugging Face Space**.
2.  Select **Docker** as the SDK.
3.  Upload or push the repository files.
4.  Ensure port **7860** is exposed in the `Dockerfile`.
5.  Add the tag **openenv** to the Space.
6.  Commit and deploy the Space.

## 🔧 Cross-Platform CLI Compatibility

A Bash wrapper named `openenv` is included to ensure that the OpenEnv
CLI is accessible in Unix-based validation environments, particularly
when using Windows virtual environments.

## 🤝 Contributing

Contributions are welcome!

1.  Fork the repository.
2.  Create a new branch: `git checkout -b feature/YourFeature`.
3.  Commit your changes: `git commit -m "Add YourFeature"`.
4.  Push to the branch: `git push origin feature/YourFeature`.
5.  Open a Pull Request.

Please ensure all tests pass before submitting your contribution.

## 🐞 Issues

If you encounter any bugs or have feature requests, please open an issue
on GitHub: 👉 https://github.com/BandariVathanSai20/soc-openenv/issues

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE`
file for more details.

## 👨‍💻 Author

**Bandari Vathan Sai**\
GitHub: https://github.com/BandariVathanSai20

## 🙌 Acknowledgements

-   **OpenEnv Team** for the benchmark and validation framework.
-   **Hugging Face** for providing deployment infrastructure.
-   The **cybersecurity community** for inspiration and domain
    knowledge.

## 📚 Citation

``` bibtex
@software{soc_openenv,
  author = {Bandari Vathan Sai},
  title = {SOC OpenEnv: Deterministic Cyber Attack Simulation Environment},
  year = {2026},
  url = {https://github.com/BandariVathanSai20/soc-openenv}
}
```

## ⭐ Support

If you found this project useful, please consider giving it a ⭐ on
GitHub to support future development!
