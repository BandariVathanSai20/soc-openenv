"""
tests/test_environment.py

Unit tests for the SOCEnv environment.
"""

import pytest
from server.environment import SOCEnv


def test_environment_reset():
    """Test that the environment resets correctly."""
    env = SOCEnv(difficulty="easy")
    observation = env.reset()

    assert observation is not None
    assert observation["step"] == 0
    assert observation["difficulty"] == "easy"
    assert env.current_step == 0
    assert env.total_reward == 0.0


def test_environment_step_progression():
    """Test that the environment progresses correctly after a step."""
    env = SOCEnv(difficulty="easy")
    env.reset()

    next_obs, reward, done, info = env.step("suspicious")

    assert isinstance(reward, float)
    assert isinstance(done, bool)
    assert isinstance(info, dict)
    assert env.current_step == 1
    assert "actual_label" in info
    assert "attack_type" in info


def test_environment_invalid_action():
    """Test that invalid actions raise an error."""
    env = SOCEnv(difficulty="easy")
    env.reset()

    with pytest.raises(ValueError):
        env.step("invalid_action")


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_environment_difficulties(difficulty):
    """Ensure all difficulty levels initialize correctly."""
    env = SOCEnv(difficulty=difficulty)
    observation = env.reset()

    assert observation["difficulty"] == difficulty
    assert env.logs is not None
    assert len(env.logs) > 0