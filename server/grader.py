"""
server/grader.py

Deterministic grader for the SOC-OpenEnv environment.
Maintains original performance while ensuring scores are strictly within (0, 1).
"""

from typing import List, Dict, Set


# ---------------------------------------------------------------------
# Ground Truth Detection
# ---------------------------------------------------------------------
def detect_ground_truth(
    log: Dict,
    failed_login_count: Dict[str, int],
    suspicious_ips: Set[str]
) -> str:
    ip = log.get("ip")

    # Brute force detection
    if log.get("event") == "login_failed":
        failed_login_count[ip] = failed_login_count.get(ip, 0) + 1
        if failed_login_count[ip] >= 3:
            return "attack"
        return "suspicious"

    # SQL Injection
    if "OR 1=1" in str(log):
        return "attack"

    # Critical access
    if log.get("level") == "CRITICAL":
        return "attack"

    # Port scan
    if log.get("event") == "port_scan":
        suspicious_ips.add(ip)
        return "suspicious"

    # Suspicious continuation
    if ip in suspicious_ips:
        return "suspicious"

    return "normal"


# ---------------------------------------------------------------------
# Step Evaluation
# ---------------------------------------------------------------------
def evaluate_step(action: str, actual: str) -> float:
    """
    Step score strictly inside (0, 1).
    Preserves original performance.
    """
    action = action.lower()
    actual = actual.lower()

    if action == actual:
        return 0.99  # High reward for correct classification

    if action == "suspicious" and actual == "attack":
        return 0.5   # Partial credit

    return 0.01      # Minimal reward, never zero


# ---------------------------------------------------------------------
# Episode Evaluation
# ---------------------------------------------------------------------
def evaluate_episode(actions: List[str], logs: List[Dict]) -> Dict[str, float]:
    """
    Compute deterministic episode metrics.
    Returns a dictionary compatible with OpenEnv validators.
    """

    if not actions or not logs:
        return {
            "normalized_score": 0.5,
            "accuracy": 0.5,
            "false_positive_rate": 0.5,
            "missed_attack_rate": 0.5,
            "early_detection_bonus": 0.5,
        }

    total_steps = min(len(actions), len(logs))
    total_score = 0.0

    failed_login_count: Dict[str, int] = {}
    suspicious_ips: Set[str] = set()
    early_detected = False
    correct = 0
    false_positives = 0
    missed_attacks = 0
    attack_count = 0

    for i, (action, log) in enumerate(zip(actions, logs)):
        actual = detect_ground_truth(
            log, failed_login_count, suspicious_ips
        )

        step_score = evaluate_step(action, actual)

        if action.lower() == actual:
            correct += 1

        if actual == "attack":
            attack_count += 1
            if action.lower() == "attack" and i <= 2:
                step_score += 0.1
                early_detected = True

        if action.lower() in {"attack", "suspicious"} and actual == "normal":
            false_positives += 1

        if action.lower() == "normal" and actual == "attack":
            missed_attacks += 1

        # Ensure step score < 1
        step_score = min(step_score, 0.99)
        total_score += step_score

    # Final normalized score (similar to original behavior)
    final_score = total_score / total_steps

    if early_detected:
        final_score += 0.02

    # Ensure strictly within (0, 1)
    final_score = max(0.01, min(final_score, 0.99))

    # Additional metrics
    accuracy = correct / total_steps
    false_positive_rate = false_positives / total_steps
    missed_attack_rate = (
        missed_attacks / attack_count if attack_count > 0 else 0.0
    )
    early_detection_bonus = 1.0 if early_detected else 0.0

    # Clip auxiliary metrics to (0,1)
    def clip(x):
        return max(0.01, min(x, 0.99))

    return {
        "normalized_score": final_score,
        "accuracy": clip(accuracy),
        "false_positive_rate": clip(false_positive_rate),
        "missed_attack_rate": clip(missed_attack_rate),
        "early_detection_bonus": clip(early_detection_bonus),
    }