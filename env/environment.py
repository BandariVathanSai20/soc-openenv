from env.tasks import get_easy_logs, get_medium_logs, get_hard_logs
from datetime import datetime


class SOCEnv:
    def __init__(self, difficulty="easy"):
        self.difficulty = difficulty

        # Base time (deterministic)
        self.base_time = datetime(2026, 1, 1, 12, 0, 0)

        self.logs = []
        self.current_step = 0
        self.history = []

        # tracking
        self.failed_login_count = {}
        self.suspicious_ips = set()
        self.attack_detected = False

    def load_logs(self):
        if self.difficulty == "easy":
            self.logs = get_easy_logs()
        elif self.difficulty == "medium":
            self.logs = get_medium_logs()
        elif self.difficulty == "hard":
            self.logs = get_hard_logs()
        else:
            raise ValueError("Invalid difficulty")

    def reset(self):
        self.load_logs()
        self.current_step = 0
        self.history = []
        self.failed_login_count = {}
        self.suspicious_ips = set()
        self.attack_detected = False

        return self.logs[self.current_step]

    # Context-aware attack detection
    def detect_attack(self, log):
        ip = log.get("ip")

        # Brute force
        if log.get("event") == "login_failed":
            self.failed_login_count[ip] = self.failed_login_count.get(ip, 0) + 1

            if self.failed_login_count[ip] >= 3:
                return "attack", "Brute Force"
            return "suspicious", "Login Attempt"

        # SQL Injection
        if "OR 1=1" in str(log):
            return "attack", "SQL Injection"

        # Critical access
        if log.get("level") == "CRITICAL":
            return "attack", "Privilege Escalation"

        # Port scan
        if log.get("event") == "port_scan":
            self.suspicious_ips.add(ip)
            return "suspicious", "Reconnaissance"

        if ip in self.suspicious_ips:
            return "suspicious", "Suspicious IP"

        return "normal", "Normal Activity"

    # Reward shaping
    def compute_reward(self, action, actual):
        reward = 0

        # correct
        if action == actual:
            reward += 1

            # early detection bonus
            if actual == "attack" and self.current_step <= 2:
                reward += 0.5
                self.attack_detected = True

        # partial
        elif action == "suspicious" and actual == "attack":
            reward += 0.4

        # false positive
        elif action == "attack" and actual == "normal":
            reward -= 1.5

        # missed attack
        elif action == "normal" and actual == "attack":
            reward -= 2

        # small penalty
        if action != "normal":
            reward -= 0.1

        return round(reward, 2)

    def step(self, action):
        log = self.logs[self.current_step].copy()

        actual, attack_type = self.detect_attack(log)

        reward = self.compute_reward(action, actual)

        # save history
        self.history.append(log)

        self.current_step += 1
        done = self.current_step >= len(self.logs)

        next_obs = None if done else self.logs[self.current_step]

        return next_obs, reward, done, {
            "attack_type": attack_type  
        }

    # State
    def state(self):
        return {
            "step": self.current_step,
            "history_length": len(self.history),
            "failed_login_attempts": self.failed_login_count,
            "suspicious_ips": list(self.suspicious_ips),
            "attack_detected": self.attack_detected,
            "difficulty": self.difficulty
        }