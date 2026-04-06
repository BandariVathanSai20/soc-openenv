from datetime import datetime, timedelta

# BASE TIME (FOR DETERMINISM)
BASE_TIME = datetime(2026, 1, 1, 12, 0, 0)


def generate_timestamp(base_time, offset):
    return (base_time + timedelta(seconds=offset)).strftime("%Y-%m-%d %H:%M:%S")


# EASY: Basic brute-force attack
def get_easy_logs():
    base_time = BASE_TIME

    return [
        {"timestamp": generate_timestamp(base_time, 1), "event": "login_failed", "ip": "192.168.1.1", "level": "WARN"},
        {"timestamp": generate_timestamp(base_time, 2), "event": "login_failed", "ip": "192.168.1.1", "level": "WARN"},
        {"timestamp": generate_timestamp(base_time, 3), "event": "login_failed", "ip": "192.168.1.1", "level": "WARN"},
        {"timestamp": generate_timestamp(base_time, 4), "event": "login_success", "ip": "192.168.1.1", "level": "INFO"},
        {"timestamp": generate_timestamp(base_time, 5), "event": "file_access", "file": "home.txt", "level": "INFO"}
    ]


# MEDIUM: Injection + normal traffic mix
def get_medium_logs():
    base_time = BASE_TIME

    return [
        {"timestamp": generate_timestamp(base_time, 1), "event": "http_request", "query": "normal search", "level": "INFO"},
        {"timestamp": generate_timestamp(base_time, 2), "event": "http_request", "query": "' OR 1=1 --", "level": "WARN"},
        {"timestamp": generate_timestamp(base_time, 3), "event": "http_request", "query": "view product", "level": "INFO"},
        {"timestamp": generate_timestamp(base_time, 4), "event": "login_success", "ip": "10.0.0.2", "level": "INFO"},
        {"timestamp": generate_timestamp(base_time, 5), "event": "file_access", "file": "profile.png", "level": "INFO"}
    ]


# HARD: Multi-stage attack chain
def get_hard_logs():
    base_time = BASE_TIME

    return [
        # Noise
        {"timestamp": generate_timestamp(base_time, 1), "event": "normal_activity", "level": "INFO"},

        # Stage 1: Recon
        {"timestamp": generate_timestamp(base_time, 2), "event": "port_scan", "ip": "10.0.0.5", "level": "WARN"},

        # Noise
        {"timestamp": generate_timestamp(base_time, 3), "event": "normal_activity", "level": "INFO"},

        # Stage 2: Brute force
        {"timestamp": generate_timestamp(base_time, 4), "event": "login_failed", "ip": "10.0.0.5", "level": "WARN"},
        {"timestamp": generate_timestamp(base_time, 5), "event": "login_failed", "ip": "10.0.0.5", "level": "WARN"},
        {"timestamp": generate_timestamp(base_time, 6), "event": "login_failed", "ip": "10.0.0.5", "level": "WARN"},

        # Stage 3: Exploit
        {"timestamp": generate_timestamp(base_time, 7), "event": "http_request", "query": "' OR 1=1 --", "level": "WARN"},

        # Stage 4: Privilege escalation
        {"timestamp": generate_timestamp(base_time, 8), "event": "file_access", "file": "/etc/passwd", "level": "CRITICAL"},

        # Noise
        {"timestamp": generate_timestamp(base_time, 9), "event": "normal_activity", "level": "INFO"},
    ]