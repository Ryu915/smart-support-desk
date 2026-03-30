PRIORITY_ORDER = ["P3", "P2", "P1", "P0"]

def upgrade(priority):
    idx = PRIORITY_ORDER.index(priority)
    return PRIORITY_ORDER[min(idx + 1, len(PRIORITY_ORDER) - 1)]


def compute_priority(impact, urgency, category, reopen_count=0):
    impact = impact.upper()
    urgency = urgency.upper()
    category = category.upper()

    base_map = {
        ("HIGH", "HIGH"): "P0",
        ("HIGH", "MEDIUM"): "P1",
        ("MEDIUM", "HIGH"): "P1",
        ("MEDIUM", "MEDIUM"): "P2",
        ("LOW", "LOW"): "P3",
    }

    priority = base_map.get((impact, urgency), "P3")

    # Category
    if category == "BUG" and priority != "P0":
        priority = upgrade(priority)

    # Reopen
    for _ in range(reopen_count):
        priority = upgrade(priority)

    return priority