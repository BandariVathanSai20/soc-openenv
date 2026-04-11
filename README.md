---
app_port: 7860
colorFrom: blue
colorTo: green
emoji: 🛡️
sdk: docker
title: SOC OpenEnv
---

# 🛡️ SOC-OpenEnv

SOC-OpenEnv is a deterministic **Security Operations Center (SOC)**
simulation environment designed to evaluate AI and reinforcement
learning agents in cybersecurity decision-making tasks. The environment
is fully compliant with the **OpenEnv** benchmark and supports
deployment both locally and on **Hugging Face Spaces** using Docker.

## 🚀 Overview

SOC-OpenEnv simulates realistic cybersecurity events such as brute-force
login attempts, SQL injection attacks, and multi-stage **Advanced
Persistent Threats (APT)**. Agents interact with the environment through
a REST API and classify each event as **normal**, **suspicious**, or
**attack**.

## ✨ Key Features

-   ✅ OpenEnv compliant and officially validated
-   🔁 Deterministic and reproducible scenarios
-   🎯 Three difficulty levels: Easy, Medium, and Hard
-   ⚡ FastAPI-based REST API
-   🐳 Dockerized deployment for Hugging Face Spaces
-   🤖 Baseline inference script for agent interaction
-   🧪 Comprehensive unit and integration tests
-   💻 Cross-platform compatibility (Windows, Linux, macOS)
-   🔧 Bash wrapper for `openenv` CLI compatibility

## 📂 Project Structure

``` text
soc-openenv/
├── server/
│   ├── app.py
│   ├── environment.py
│   ├── grader.py
│   ├── models.py
│   └── tasks.py
├── tests/
│   ├── test_api.py
│   ├── test_environment.py
│   └── test_grader.py
├── scripts/
│   └── validate-submission.sh
├── inference.py
├── client.py
├── scenario_config.json
├── openenv.yaml
├── openenv
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── pyproject.toml
├── README.md
└── .gitignore
```

## 🧠 Environment Description

### 🔍 Observation Space

Each step returns a structured log entry containing:

  Field          Description
  -------------- ------------------------------------------------------------
  `event`        Type of event (e.g., `login_failed`, `query`, `port_scan`)
  `timestamp`    ISO 8601 timestamp
  `ip`           Source IP address
  `query`        SQL query (if applicable)
  `file`         Accessed file (if applicable)
  `level`        Severity level
  `step`         Current step in the episode
  `difficulty`   Scenario difficulty

### 🎮 Action Space

  Action         Description
  -------------- --------------------------------
  `normal`       Benign activity
  `suspicious`   Potentially malicious activity
  `attack`       Confirmed malicious activity

## 🎯 Scenarios

  ------------------------------------------------------------------------
  Difficulty                Scenario           Description
  ------------------------- ------------------ ---------------------------
  Easy                      Brute Force        Detect repeated failed
                            Detection          login attempts

  Medium                    SQL Injection      Identify malicious SQL
                                               queries

  Hard                      Multi-Stage APT    Detect reconnaissance and
                                               persistence activities
  ------------------------------------------------------------------------

## 📊 Grading Scheme

The SOC-OpenEnv environment uses a deterministic grading mechanism:

| Scenario | Score |
|---------|------|
| Correct classification | 0.90 |
| Suspicious instead of attack | 0.50 |
| Incorrect classification | 0.10 |
| Early attack detection (≤ step 2) | +0.05 |

The final **normalized score** is the average of all step scores, clamped to the range [0, 1].

## 📊 Baseline Performance

The baseline agent was evaluated across all difficulty levels with the following deterministic scores:

| Difficulty | Score |
|-----------|------|
| Easy      | 0.91 |
| Medium    | 0.75 |
| Hard      | 0.90 |

These scores demonstrate the environment’s ability to differentiate agent performance across varying levels of complexity.

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
