"""
server/environment.py

SOCEnv: Security Operations Center (SOC) simulation environment
for the OpenEnv RL Challenge.

This environment simulates real-world cyber attack scenarios such as:
- Brute-force login attempts
- SQL injection
- Port scanning (reconnaissance)
- Privilege escalation

It follows the OpenEnv specification with the required methods:
- reset()
- step(action)
- state()
- close()
"""

from datetime import datetime
from typing import Dict, Tuple, List, Set, Optional
from server.tasks import get_easy_logs, get_medium_logs, get_hard_logs


VALID_ACTIONS = {"normal", "suspicious", "attack"}


class SOCEnv:
    """
    Security Operations Center (SOC) simulation environment.
    """

    def __init__(self, difficulty: str = "easy", seed: Optional[int] = 42):
        """
        Initialize the SOC environment.

        Args:
            difficulty (str): Difficulty level ('easy', 'medium', 'hard').
            seed (Optional[int]): Random seed for reproducibility.
        """
        if difficulty not in {"easy", "medium", "hard"}:
            raise ValueError("Invalid difficulty. Choose from 'easy', 'medium', or 'hard'.")

        self.difficulty: str = difficulty
        self.seed: Optional[int] = seed
        self.base_time: datetime = datetime(2026, 1, 1, 12, 0, 0)

        # Environment data
        self.logs: List[Dict] = []
        self.current_step: int = 0
        self.history: List[Dict] = []

        # Stateful tracking
        self.failed_login_count: Dict[str, int] = {}
        self.suspicious_ips: Set[str] = set()
        self.attack_detected: bool = False
        self.total_reward: float = 0.0

        # Reward normalization parameters
        self.max_reward_per_step: float = 1.5  # Matches openenv.yaml
        self.min_reward_per_step: float = -2.0

    # Load Logs
    def load_logs(self) -> None:
        """Load logs based on the selected difficulty."""
        if self.difficulty == "easy":
            self.logs = get_easy_logs()
        elif self.difficulty == "medium":
            self.logs = get_medium_logs()
        else:
            self.logs = get_hard_logs()

        if not self.logs:
            raise ValueError("No logs available for the selected difficulty.")

    # Reset Environment
    def reset(self) -> Dict:
        """
        Reset the environment to its initial state.

        Returns:
            Dict: Initial observation.
        """
        self.load_logs()
        self.current_step = 0
        self.history = []
        self.failed_login_count = {}
        self.suspicious_ips = set()
        self.attack_detected = False
        self.total_reward = 0.0

        return self._format_observation(self.logs[self.current_step])

    # Format Observation
    def _format_observation(self, log: Dict) -> Dict:
        """
        Format the observation to match the OpenEnv observation space.

        Args:
            log (Dict): Raw log entry.

        Returns:
            Dict: Formatted observation.
        """
        return {
            "event": log.get("event"),
            "timestamp": log.get("timestamp", self.base_time.isoformat()),
            "ip": log.get("ip"),
            "query": log.get("query"),
            "file": log.get("file"),
            "level": log.get("level"),
            "step": self.current_step,
            "difficulty": self.difficulty,
        }

    # Ground Truth Detection
    def detect_attack(self, log: Dict) -> Tuple[str, str]:
        """
        Determine the ground truth classification of a log entry.

        Returns:
            Tuple[str, str]: (actual_label, attack_type)
        """
        ip = log.get("ip")
        event = log.get("event")
        query = str(log.get("query", "")).lower()
        level = log.get("level")

        # Brute Force Detection
        if event == "login_failed":
            self.failed_login_count[ip] = self.failed_login_count.get(ip, 0) + 1
            if self.failed_login_count[ip] >= 3:
                return "attack", "Brute Force"
            return "suspicious", "Login Attempt"

        # SQL Injection Detection
        sqli_patterns = ["or 1=1", "'--", "union select", "sleep("]
        if any(pattern in query for pattern in sqli_patterns):
            return "attack", "SQL Injection"

        # Privilege Escalation Detection
        if level == "CRITICAL":
            return "attack", "Privilege Escalation"

        # Port Scan Detection
        if event == "port_scan":
            self.suspicious_ips.add(ip)
            return "suspicious", "Reconnaissance"

        # Suspicious Continuation
        if ip in self.suspicious_ips:
            return "suspicious", "Suspicious IP"

        return "normal", "Normal Activity"

    # Reward Function
    def compute_reward(self, action: str, actual: str) -> float:
        """
        Compute the reward based on the agent's action.

        Args:
            action (str): Agent's classification.
            actual (str): Ground truth label.

        Returns:
            float: Reward value.
        """
        reward = 0.0

        # Correct classification
        if action == actual:
            reward += 1.0
            if actual == "attack" and self.current_step <= 2:
                reward += 0.4  # Early detection bonus
                self.attack_detected = True

        # Partial credit
        elif action == "suspicious" and actual == "attack":
            reward += 0.4

        # False positive
        elif action == "attack" and actual == "normal":
            reward -= 1.5

        # Missed attack
        elif action == "normal" and actual == "attack":
            reward -= 2.0

        # Small penalty for over-alerting
        if action != "normal":
            reward -= 0.1

        # Clamp reward within defined range
        reward = max(self.min_reward_per_step, min(self.max_reward_per_step, reward))
        reward = round(reward, 2)

        self.total_reward += reward
        return reward

    # Step Function
    def step(self, action: str) -> Tuple[Optional[Dict], float, bool, Dict]:
        """
        Execute one step in the environment.

        Args:
            action (str): Agent action ('normal', 'suspicious', 'attack').

        Returns:
            Tuple containing:
                - next observation (Dict or None)
                - reward (float)
                - done (bool)
                - info (Dict)
        """
        if action not in VALID_ACTIONS:
            raise ValueError(
                f"Invalid action '{action}'. Valid actions are: {VALID_ACTIONS}"
            )

        if self.current_step >= len(self.logs):
            raise RuntimeError("Episode already completed.")

        log = self.logs[self.current_step].copy()
        actual_label, attack_type = self.detect_attack(log)
        reward = self.compute_reward(action, actual_label)

        self.history.append(log)
        self.current_step += 1
        done = self.current_step >= len(self.logs)

        next_obs = (
            None
            if done
            else self._format_observation(self.logs[self.current_step])
        )

        info = {
            "attack_type": attack_type,
            "actual_label": actual_label,
            "total_reward": round(self.total_reward, 2),
            "normalized_score": self.normalized_score(),
        }

        return next_obs, reward, done, info

    # Normalized Score
    def normalized_score(self) -> float:
        """
        Compute a normalized score between 0.0 and 1.0.
        """
        max_possible_reward = len(self.logs) * self.max_reward_per_step
        if max_possible_reward == 0:
            return 0.0
        score = self.total_reward / max_possible_reward
        return round(max(0.0, min(1.0, score)), 3)

    # State Function
    def state(self) -> Dict:
        """
        Return the current internal state of the environment.
        """
        return {
            "step": self.current_step,
            "history_length": len(self.history),
            "failed_login_attempts": self.failed_login_count,
            "suspicious_ips": list(self.suspicious_ips),
            "attack_detected": self.attack_detected,
            "difficulty": self.difficulty,
            "total_reward": round(self.total_reward, 2),
            "normalized_score": self.normalized_score(),
        }

    # Close Function
    def close(self) -> None:
        """
        Cleanup resources (if any). Included for OpenEnv compatibility.
        """
        pass