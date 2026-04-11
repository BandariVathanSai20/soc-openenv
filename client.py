"""
client.py

Simple client script to interact with the SOC-OpenEnv API.
Useful for manual testing and demonstrations.
"""

import requests
from typing import Dict, Any


class SOCClient:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url

    def reset(self, difficulty: str = "easy") -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/reset",
            json={"difficulty": difficulty},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def step(self, action: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/step",
            json={"action": action},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def state(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/state", timeout=10)
        response.raise_for_status()
        return response.json()

    def health(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/health", timeout=10)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    client = SOCClient()

    print("🔄 Resetting environment...")
    reset_data = client.reset("easy")
    print("Initial Observation:", reset_data["observation"])

    print("\n➡️ Taking a step...")
    step_data = client.step("suspicious")
    print("Step Response:", step_data)

    print("\n📊 Current State:")
    print(client.state())

    print("\n❤️ Health Check:")
    print(client.health())