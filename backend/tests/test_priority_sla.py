from app.services.priority_engine import compute_priority
from app.services.sla_engine import calculate_deadline
from datetime import datetime, timedelta


def test_priority_high_high():
    assert compute_priority("HIGH", "HIGH", "BUG") == "P0"


def test_priority_bug_bump():
    assert compute_priority("MEDIUM", "MEDIUM", "BUG") == "P1"


def test_reopen_escalation():
    assert compute_priority("LOW", "LOW", "OTHER", reopen_count=2) == "P1"


def test_sla_deadline():
    now = datetime.utcnow()
    deadline = calculate_deadline("P1", now)
    assert deadline == now + timedelta(hours=12)