from typing import Dict, Tuple, List, Optional
from server.tasks import get_easy_logs, get_medium_logs, get_hard_logs

VALID_ACTIONS = {"normal", "suspicious", "attack"}

class SOCEnv:
    def __init__(self, difficulty: str = "easy"):
        self.difficulty = difficulty
        self.reset()

    def reset(self):
        if self.difficulty == "easy": self.logs = get_easy_logs()
        elif self.difficulty == "medium": self.logs = get_medium_logs()
        else: self.logs = get_hard_logs()
        
        self.current_step = 0
        self.total_reward = 0.0
        self.actions = []
        self.failed_counts = {}
        return self._obs()

    def _obs(self):
        log = self.logs[self.current_step].copy()
        log["step"] = self.current_step
        log["difficulty"] = self.difficulty
        return log

    def step(self, action: str) -> Tuple[Optional[Dict], float, bool, Dict]:
        # Added Validation to fix the failing test
        if not action or action.lower() not in VALID_ACTIONS:
            raise ValueError(f"Invalid action: {action}. Must be one of {VALID_ACTIONS}")

        from server.grader import get_ground_truth
        
        current_log = self.logs[self.current_step]
        actual = get_ground_truth(current_log, self.failed_counts)
        
        # Reward Logic
        reward = 1.0 if action.lower() == actual else -1.0
        self.total_reward += reward
        self.actions.append(action)
        
        self.current_step += 1
        done = self.current_step >= len(self.logs)
        next_obs = self._obs() if not done else None
        
        info = {"actual_label": actual, "attack_type": "security_event"}
        return next_obs, float(reward), done, info

    def state(self):
        return {
            "step": self.current_step, 
            "total_reward": round(self.total_reward, 2), 
            "difficulty": self.difficulty
        }