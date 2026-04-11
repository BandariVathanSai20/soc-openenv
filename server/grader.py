"""
server/grader.py

Final grader for the SOC-OpenEnv environment.
This implementation mirrors the logic used in SOCEnv.detect_attack()
and ensures all returned metrics are strictly within the open interval (0, 1).
"""

from typing import List, Dict, Tuple

EPS = 1e-3  # Prevents scores from being exactly 0 or 1


def _clip_open_interval(value: float) -> float:
    """Ensure a value lies strictly within the open interval (0, 1)."""
    if value <= 0.0:
        return EPS
    if value >= 1.0:
        return 1.0 - EPS
    return value


def _detect_attack(
    log: Dict,
    failed_login_count: Dict[str, int],
    suspicious_ips: set
) -> Tuple[str, str]:
    """
    Replicates the SOCEnv.detect_attack() logic to determine
    the actual label and attack type.
    """
    event = str(log.get("event", "")).lower()
    level = str(log.get("level", "")).lower()
    message = str(log).lower()
    ip = log.get("ip", "unknown")

    # SQL Injection
    if "or 1=1" in message:
        return "attack", "sql_injection"

    # Critical severity events
    if level == "critical":
        return "attack", "critical_event"

    # Brute-force login detection
    if event == "login_failed":
        failed_login_count[ip] = failed_login_count.get(ip, 0) + 1
        if failed_login_count[ip] >= 3:
            return "attack", "brute_force"
        return "suspicious", "brute_force_attempt"

    # Port scan detection
    if event == "port_scan":
        suspicious_ips.add(ip)
        return "suspicious", "port_scan"

    # Continued suspicious behavior
    if ip in suspicious_ips:
        return "suspicious", "related_activity"

    # Normal activity
    if event == "login_success":
        return "normal", "normal_activity"

    return "normal", "unknown"


def evaluate_episode(actions: List[str], logs: List[Dict]) -> Dict[str, float]:
    """
    Evaluate the agent's performance over an episode.
    Returns metrics strictly within the open interval (0, 1).
    """

    # Handle empty inputs gracefully
    if not actions or not logs:
        return {
            "normalized_score": 0.5,
            "accuracy": 0.5,
            "false_positive_rate": 0.5,
            "missed_attack_rate": 0.5,
            "early_detection_bonus": 0.5,
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
        actual_label, _ = _detect_attack(
            logs[i],
            failed_login_count,
            suspicious_ips
        )

        if actual_label == "attack":
            attack_count += 1

        if action == actual_label:
            correct += 1
            # Bonus for early attack detection
            if actual_label == "attack" and i < 2:
                early_detection += 1
        else:
            if action in {"attack", "suspicious"} and actual_label == "normal":
                false_positives += 1
            if action == "normal" and actual_label == "attack":
                missed_attacks += 1

    accuracy = correct / total
    false_positive_rate = false_positives / total
    missed_attack_rate = (
        missed_attacks / attack_count if attack_count > 0 else 0.0
    )
    early_detection_bonus = early_detection / total

    # Composite normalized score aligned with environment performance
    normalized_score = (
        0.7 * accuracy
        + 0.1 * (1 - false_positive_rate)
        + 0.1 * (1 - missed_attack_rate)
        + 0.1 * early_detection_bonus
    )

    return {
        "normalized_score": _clip_open_interval(normalized_score),
        "accuracy": _clip_open_interval(accuracy),
        "false_positive_rate": _clip_open_interval(false_positive_rate),
        "missed_attack_rate": _clip_open_interval(missed_attack_rate),
        "early_detection_bonus": _clip_open_interval(early_detection_bonus),
    }