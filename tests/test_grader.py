"""
tests/test_grader.py

Unit tests for the SOC grader.
"""

from server.grader import evaluate_episode


def test_grader_returns_valid_metrics():
    """Ensure the grader returns metrics within valid ranges."""
    actions = ["suspicious", "attack", "normal"]
    logs = [
        {"event": "login_failed", "ip": "1.1.1.1", "level": "INFO"},
        {"event": "login_failed", "ip": "1.1.1.1", "level": "INFO"},
        {"event": "login_success", "ip": "2.2.2.2", "level": "INFO"},
    ]

    metrics = evaluate_episode(actions, logs)

    assert isinstance(metrics, dict)
    assert 0.0 <= metrics["normalized_score"] <= 1.0
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["false_positive_rate"] <= 1.0
    assert 0.0 <= metrics["missed_attack_rate"] <= 1.0
    assert 0.0 <= metrics["early_detection_bonus"] <= 1.0


def test_grader_handles_empty_inputs():
    """Ensure the grader handles empty inputs gracefully."""
    metrics = evaluate_episode([], [])
    assert metrics["normalized_score"] == 0.5