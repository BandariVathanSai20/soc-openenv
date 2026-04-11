# server/grader.py

from typing import List, Dict

EPS = 1e-3  # Ensures values are strictly within (0, 1)


def _clip(value: float) -> float:
    """Clip values to the open interval (0, 1)."""
    if value <= 0.0:
        return EPS
    if value >= 1.0:
        return 1.0 - EPS
    return float(value)


def _detect_attack(log: Dict, failed_login_count: Dict[str, int], suspicious_ips: set) -> str:
    """Replicates SOCEnv's ground-truth logic."""
    event = str(log.get("event", "")).lower()
    level = str(log.get("level", "")).lower()
    message = str(log).lower()
    ip = log.get("ip", "unknown")

    if "or 1=1" in message or level == "critical":
        return "attack"

    if event == "login_failed":
        failed_login_count[ip] = failed_login_count.get(ip, 0) + 1
        if failed_login_count[ip] >= 3:
            return "attack"
        return "suspicious"

    if event == "port_scan":
        suspicious_ips.add(ip)
        return "suspicious"

    if ip in suspicious_ips:
        return "suspicious"

    if event == "login_success":
        return "normal"

    return "normal"


def evaluate_episode(actions: List[str], logs: List[Dict]) -> Dict[str, float]:
    """Evaluate episode performance with all metrics strictly in (0, 1)."""

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
        actual = _detect_attack(logs[i], failed_login_count, suspicious_ips)

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

    accuracy = correct / total
    false_positive_rate = false_positives / total
    missed_attack_rate = (
        missed_attacks / attack_count if attack_count > 0 else 0.0
    )
    early_detection_bonus = early_detection / total

    normalized_score = (
        0.6 * accuracy
        + 0.15 * (1 - false_positive_rate)
        + 0.15 * (1 - missed_attack_rate)
        + 0.10 * early_detection_bonus
    )

    # Final clipping to ensure strict bounds
    return {
        "normalized_score": _clip(normalized_score),
        "accuracy": _clip(accuracy),
        "false_positive_rate": _clip(false_positive_rate),
        "missed_attack_rate": _clip(missed_attack_rate),
        "early_detection_bonus": _clip(early_detection_bonus),
    }