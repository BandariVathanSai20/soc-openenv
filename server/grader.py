"""
server/grader.py

Final grader for the SOC-OpenEnv environment.
Ensures all returned metrics are strictly within the open interval (0, 1),
as required by the OpenEnv Hackathon validator.
"""

from typing import List, Dict

EPS = 1e-6

def _clip_open_interval(value: float) -> float:
    if value <= 0.0:
        return EPS
    if value >= 1.0:
        return 1.0 - EPS
    return value


def _detect_attack(
    log: Dict,
    failed_login_count: Dict[str, int],
    suspicious_ips: set
) -> str:
    """
    Mirror the SOCEnv.detect_attack() logic to determine
    the ground-truth label for each log entry.
    """
    event = str(log.get("event", "")).lower()
    level = str(log.get("level", "")).lower()
    message = str(log).lower()
    ip = log.get("ip", "unknown")

    # SQL Injection
    if "or 1=1" in message:
        return "attack"

    # Critical severity
    if level == "critical":
        return "attack"

    # Brute-force login detection
    if event == "login_failed":
        failed_login_count[ip] = failed_login_count.get(ip, 0) + 1
        if failed_login_count[ip] >= 3:
            return "attack"
        return "suspicious"

    # Port scan detection
    if event == "port_scan":
        suspicious_ips.add(ip)
        return "suspicious"

    # Continued suspicious behavior
    if ip in suspicious_ips:
        return "suspicious"

    # Normal activity
    if event == "login_success":
        return "normal"

    return "normal"


def evaluate_episode(actions: List[str], logs: List[Dict]) -> Dict[str, float]:
    """
    Evaluate the agent's performance over an episode and return metrics
    strictly within the open interval (0, 1).
    """

    # Handle empty inputs gracefully
    if not actions or not logs:
        mid = 0.5
        return {
            "normalized_score": mid,
            "accuracy": mid,
            "false_positive_rate": mid,
            "missed_attack_rate": mid,
            "early_detection_bonus": mid,
        }

    total = min(len(actions), len(logs))
    correct = 0
    false_positives = 0
    missed_attacks = 0
    early_detection = 0
    attack_count = 0

    failed_login_count: Dict[str, int] = {}
    suspicious_ips = set()

    for i in range(total):
        action = actions[i].lower()
        actual = _detect_attack(
            logs[i],
            failed_login_count,
            suspicious_ips
        )

        if actual == "attack":
            attack_count += 1

        if action == actual:
            correct += 1
            if actual == "attack" and i < 2:
                early_detection += 1
        else:
            if action in {"attack", "suspicious"} and actual == "normal":
                false_positives += 1
            if action == "normal" and actual == "attack":
                missed_attacks += 1

    # Raw metrics
    accuracy = correct / total
    false_positive_rate = false_positives / total
    missed_attack_rate = (
        missed_attacks / attack_count if attack_count > 0 else 0.0
    )
    early_detection_bonus = early_detection / total

    # Composite normalized score
    normalized_score = (
        0.6 * accuracy
        + 0.15 * (1 - false_positive_rate)
        + 0.15 * (1 - missed_attack_rate)
        + 0.10 * early_detection_bonus
    )

    # Ensure all metrics are strictly within (0, 1)
    return {
        "normalized_score": _clip_open_interval(normalized_score),
        "accuracy": _clip_open_interval(accuracy),
        "false_positive_rate": _clip_open_interval(false_positive_rate),
        "missed_attack_rate": _clip_open_interval(missed_attack_rate),
        "early_detection_bonus": _clip_open_interval(early_detection_bonus),
    }