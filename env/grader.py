def detect_ground_truth(log, failed_login_count, suspicious_ips):
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


def evaluate_step(action, actual):
    """
    Step score STRICTLY inside (0,1)
    """

    if action == actual:
        return 0.95   # reduced from 0.99

    if action == "suspicious" and actual == "attack":
        return 0.5

    return 0.05   # never 0


def evaluate_episode(actions, logs):
    """
    Deterministic episode scoring STRICTLY in (0,1)
    """

    total_score = 0.0
    total_steps = len(logs)

    failed_login_count = {}
    suspicious_ips = set()

    early_detected = False

    for i, (action, log) in enumerate(zip(actions, logs)):

        actual = detect_ground_truth(
            log, failed_login_count, suspicious_ips
        )

        step_score = evaluate_step(action, actual)

        # Controlled bonus
        if actual == "attack" and action == "attack" and i <= 2:
            step_score += 0.1   # reduced from 0.2
            early_detected = True

        # HARD CAP per step
        if step_score >= 1.0:
            step_score = 0.99

        total_score += step_score

    final_score = total_score / total_steps

    # Controlled global bonus
    if early_detected:
        final_score += 0.02   # reduced from 0.05

    # STRICT CLAMP
    if final_score >= 1.0:
        final_score = 0.99
    elif final_score <= 0.0:
        final_score = 0.01

    return final_score
