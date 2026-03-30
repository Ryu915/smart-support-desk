from app.services.priority_engine import compute_priority
from app.services.sla_engine import calculate_deadline
from app.routers.tickets import can_transition
from app.routers.dashboard import seconds_to_hours
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


def test_status_transition_validation():
    assert can_transition("OPEN", "IN_PROGRESS") is True
    assert can_transition("OPEN", "CLOSED") is False


def test_dashboard_average_resolution_hours():
    assert seconds_to_hours(7200) == 2.0