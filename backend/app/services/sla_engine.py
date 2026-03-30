from datetime import datetime, timedelta

SLA_RULES = {
    "P0": 4,
    "P1": 12,
    "P2": 24,
    "P3": 72,
}

def calculate_deadline(priority, created_at):
    hours = SLA_RULES.get(priority, 72)
    return created_at + timedelta(hours=hours)


def get_sla_status(deadline):
    now = datetime.utcnow()

    if now > deadline:
        return {
            "status": "OVERDUE",
            "overdue_by": str(now - deadline)
        }
    else:
        return {
            "status": "ON_TIME",
            "remaining": str(deadline - now)
        }