# tests/test_grader.py

from server.grader import evaluate_episode


def test_episode_score_within_open_interval():
    actions = ["suspicious", "attack", "normal"]
    logs = [
        {"event": "login_failed", "ip": "1.1.1.1", "level": "INFO"},
        {"event": "login_failed", "ip": "1.1.1.1", "level": "INFO"},
        {"event": "login_success", "ip": "2.2.2.2", "level": "INFO"},
    ]

    score = evaluate_episode(actions, logs)

    assert isinstance(score, float)
    assert 0.0 < score < 1.0