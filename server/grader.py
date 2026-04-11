"""
server/grader.py

Deterministic grading logic for the SOC-OpenEnv environment.
This module evaluates agent actions against ground truth labels
and computes both step-level and episode-level performance metrics.
"""

from typing import List, Dict, Tuple, Set


VALID_ACTIONS = {"normal", "suspicious", "attack"}


# Ground Truth Detection 
def detect_ground_truth(
    log: Dict,
    failed_login_count: Dict[str, int],
    suspicious_ips: Set[str],
) -> Tuple[str, str]:
    """
    Determine the ground truth classification of a log entry.

    Args:
        log (Dict): Log entry.
        failed_login_count (Dict[str, int]): Stateful tracking of failed logins.
        suspicious_ips (Set[str]): Set of suspicious IPs.

    Returns:
        Tuple[str, str]: (actual_label, attack_type)
    """
    ip = log.get("ip")
    event = log.get("event")
    query = str(log.get("query", "")).lower()
    level = log.get("level")

    # Brute Force Detection
    if event == "login_failed":
        failed_login_count[ip] = failed_login_count.get(ip, 0) + 1
        if failed_login_count[ip] >= 3:
            return "attack", "Brute Force"
        return "suspicious", "Login Attempt"

    # SQL Injection Detection (case-insensitive)
    sqli_patterns = ["or 1=1", "'--", "union select", "sleep("]
    if any(pattern in query for pattern in sqli_patterns):
        return "attack", "SQL Injection"

    # Privilege Escalation
    if level == "CRITICAL":
        return "attack", "Privilege Escalation"

    # Port Scan Detection
    if event == "port_scan":
        suspicious_ips.add(ip)
        return "suspicious", "Reconnaissance"

    # Suspicious Continuation
    if ip in suspicious_ips:
        return "suspicious", "Suspicious IP"

    return "normal", "Normal Activity"


# Step-Level Evaluation
def evaluate_step(
    action: str,
    actual: str,
    step_index: int,
) -> Tuple[float, bool]:
    """
    Evaluate a single step.

    Args:
        action (str): Agent action.
        actual (str): Ground truth label.
        step_index (int): Step index in the episode.

    Returns:
        Tuple[float, bool]: (step_score, early_detection_flag)
    """
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid action '{action}'. Valid actions: {VALID_ACTIONS}")

    early_detection = False

    # Base scoring
    if action == actual:
        score = 0.9
    elif action == "suspicious" and actual == "attack":
        score = 0.5
    else:
        score = 0.1

    # Early detection bonus
    if actual == "attack" and action == "attack" and step_index <= 2:
        score += 0.05
        early_detection = True

    return min(score, 1.0), early_detection


# Episode-Level Evaluation
def evaluate_episode(
    actions: List[str],
    logs: List[Dict],
) -> Dict[str, float]:
    """
    Evaluate an entire episode.

    Args:
        actions (List[str]): List of agent actions.
        logs (List[Dict]): Corresponding list of environment logs.

    Returns:
        Dict[str, float]: Dictionary containing evaluation metrics.
    """
    if not actions or not logs:
        return {
            "normalized_score": 0.5,
            "accuracy": 0.0,
            "false_positive_rate": 0.0,
            "missed_attack_rate": 0.0,
            "early_detection_bonus": 0.0,
        }

    failed_login_count: Dict[str, int] = {}
    suspicious_ips: Set[str] = set()

    total_score = 0.0
    correct = 0
    false_positives = 0
    missed_attacks = 0
    total_normals = 0
    total_attacks = 0
    early_detections = 0
    total_steps = 0

    for idx, (action, log) in enumerate(zip(actions, logs)):
        if log is None:
            continue

        actual_label, _ = detect_ground_truth(
            log, failed_login_count, suspicious_ips
        )

        step_score, early_flag = evaluate_step(action, actual_label, idx)
        total_score += step_score
        total_steps += 1

        # Accuracy
        if action == actual_label:
            correct += 1

        # False positives
        if actual_label == "normal":
            total_normals += 1
            if action == "attack":
                false_positives += 1

        # Missed attacks
        if actual_label == "attack":
            total_attacks += 1
            if action == "normal":
                missed_attacks += 1

        # Early detections
        if early_flag:
            early_detections += 1

    if total_steps == 0:
        normalized_score = 0.5
    else:
        normalized_score = total_score / total_steps

    accuracy = correct / total_steps if total_steps > 0 else 0.0
    false_positive_rate = (
        false_positives / total_normals if total_normals > 0 else 0.0
    )
    missed_attack_rate = (
        missed_attacks / total_attacks if total_attacks > 0 else 0.0
    )
    early_detection_bonus = early_detections / total_attacks if total_attacks > 0 else 0.0

    # Clamp normalized score to [0, 1]
    normalized_score = max(0.0, min(1.0, normalized_score))

    return {
        "normalized_score": round(normalized_score, 2),
        "accuracy": round(accuracy, 2),
        "false_positive_rate": round(false_positive_rate, 2),
        "missed_attack_rate": round(missed_attack_rate, 2),
        "early_detection_bonus": round(early_detection_bonus, 2),
    }