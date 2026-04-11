"""
server/grader.py

Grader for evaluating agent performance in the SOC-OpenEnv environment.
Ensures all metrics fall strictly within the open interval (0, 1).
"""

from typing import List, Dict


def _clip_score(value: float, eps: float = 1e-6) -> float:
    """
    Ensure the score lies strictly within the open interval (0, 1).
    """
    if value <= 0.0:
        return eps
    if value >= 1.0:
        return 1.0 - eps
    return value


def evaluate_episode(actions: List[str], logs: List[Dict]) -> Dict[str, float]:
    """
    Evaluate the agent's performance over an episode.

    Returns a dictionary with:
    - normalized_score
    - accuracy
    - false_positive_rate
    - missed_attack_rate
    - early_detection_bonus
    All values are guaranteed to be strictly within (0, 1).
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

    # Simple heuristic labeling based on log events
    for i in range(total):
        log = logs[i]
        action = actions[i].lower()

        event = log.get("event", "")
        actual_label = "attack" if "failed" in event else "normal"

        if action == actual_label:
            correct += 1
            if actual_label == "attack":
                early_detection += 1
        else:
            if action in {"attack", "suspicious"} and actual_label == "normal":
                false_positives += 1
            if action == "normal" and actual_label == "attack":
                missed_attacks += 1

    accuracy = correct / total
    false_positive_rate = false_positives / total
    missed_attack_rate = missed_attacks / total
    early_detection_bonus = early_detection / total

    # Composite normalized score
    normalized_score = (
        0.5 * accuracy
        + 0.2 * (1 - false_positive_rate)
        + 0.2 * (1 - missed_attack_rate)
        + 0.1 * early_detection_bonus
    )

    # Clip all metrics to ensure they are strictly within (0, 1)
    return {
        "normalized_score": _clip_score(normalized_score),
        "accuracy": _clip_score(accuracy),
        "false_positive_rate": _clip_score(false_positive_rate),
        "missed_attack_rate": _clip_score(missed_attack_rate),
        "early_detection_bonus": _clip_score(early_detection_bonus),
    }