"""
server/tasks.py

Deterministic SOC log generators for the SOC-OpenEnv environment.
Each function returns a list of log dictionaries representing
different cybersecurity scenarios across three difficulty levels:
easy, medium, and hard.
"""

from typing import List, Dict, Optional


# Helper Function to Create Log Entries
def create_log(
    timestamp: str,
    event: str,
    ip: str,
    level: str,
    query: Optional[str] = None,
    file: Optional[str] = None,
    label: Optional[str] = None,
) -> Dict:
    """
    Create a standardized SOC log entry.

    Args:
        timestamp (str): ISO 8601 timestamp.
        event (str): Type of event.
        ip (str): Source IP address.
        level (str): Severity level (INFO, WARNING, CRITICAL).
        query (Optional[str]): SQL query if applicable.
        file (Optional[str]): File accessed if applicable.
        label (Optional[str]): Ground truth classification for debugging.

    Returns:
        Dict: Structured log entry.
    """
    return {
        "timestamp": timestamp,
        "event": event,
        "ip": ip,
        "level": level,
        "query": query,
        "file": file,
        "label": label,  # Optional ground truth for debugging/evaluation
    }


# Easy Task: Brute Force Detection
def get_easy_logs() -> List[Dict]:
    """
    Easy scenario focusing on brute-force login detection.
    The agent must identify repeated failed login attempts
    from the same IP address.
    """
    return [
        create_log(
            "2026-01-01T12:00:00",
            "login_failed",
            "192.168.1.10",
            "INFO",
            label="suspicious",
        ),
        create_log(
            "2026-01-01T12:01:00",
            "login_failed",
            "192.168.1.10",
            "INFO",
            label="suspicious",
        ),
        create_log(
            "2026-01-01T12:02:00",
            "login_failed",
            "192.168.1.10",
            "INFO",
            label="attack",  # Third attempt triggers brute-force detection
        ),
        create_log(
            "2026-01-01T12:03:00",
            "login_success",
            "192.168.1.5",
            "INFO",
            label="normal",
        ),
        # Benign noise
        create_log(
            "2026-01-01T12:04:00",
            "file_access",
            "192.168.1.15",
            "INFO",
            file="/home/user/document.txt",
            label="normal",
        ),
    ]


# Medium Task: SQL Injection Detection
def get_medium_logs() -> List[Dict]:
    """
    Medium scenario focusing on SQL injection detection
    within mixed normal and suspicious traffic.
    """
    return [
        create_log(
            "2026-01-01T12:00:00",
            "query",
            "192.168.1.20",
            "INFO",
            query="SELECT * FROM users",
            label="normal",
        ),
        create_log(
            "2026-01-01T12:01:00",
            "query",
            "192.168.1.21",
            "WARNING",
            query="SELECT * FROM users WHERE id=1 OR 1=1",
            label="attack",
        ),
        create_log(
            "2026-01-01T12:02:00",
            "login_success",
            "192.168.1.22",
            "INFO",
            label="normal",
        ),
        # Additional benign traffic
        create_log(
            "2026-01-01T12:03:00",
            "file_access",
            "192.168.1.23",
            "INFO",
            file="/var/www/index.html",
            label="normal",
        ),
        # Suspicious but not confirmed attack
        create_log(
            "2026-01-01T12:04:00",
            "query",
            "192.168.1.24",
            "WARNING",
            query="SELECT password FROM users",
            label="suspicious",
        ),
    ]


# Hard Task: Multi-Stage APT Detection
def get_hard_logs() -> List[Dict]:
    """
    Hard scenario simulating a multi-stage Advanced Persistent Threat (APT)
    involving reconnaissance, brute-force login attempts, exploitation,
    and privilege escalation.
    """
    return [
        # Reconnaissance: Port scanning
        create_log(
            "2026-01-01T12:00:00",
            "port_scan",
            "192.168.1.30",
            "WARNING",
            label="suspicious",
        ),
        # Brute-force login attempts
        create_log(
            "2026-01-01T12:01:00",
            "login_failed",
            "192.168.1.30",
            "INFO",
            label="suspicious",
        ),
        create_log(
            "2026-01-01T12:02:00",
            "login_failed",
            "192.168.1.30",
            "INFO",
            label="suspicious",
        ),
        create_log(
            "2026-01-01T12:03:00",
            "login_failed",
            "192.168.1.30",
            "INFO",
            label="attack",
        ),
        # Lateral movement / exploitation
        create_log(
            "2026-01-01T12:04:00",
            "file_access",
            "192.168.1.30",
            "WARNING",
            file="/etc/passwd",
            label="suspicious",
        ),
        # Privilege escalation
        create_log(
            "2026-01-01T12:05:00",
            "file_access",
            "192.168.1.30",
            "CRITICAL",
            file="/root/.ssh/id_rsa",
            label="attack",
        ),
        # Benign activity for noise
        create_log(
            "2026-01-01T12:06:00",
            "login_success",
            "192.168.1.40",
            "INFO",
            label="normal",
        ),
    ]