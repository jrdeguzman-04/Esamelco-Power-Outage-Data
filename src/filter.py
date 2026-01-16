# power_filter.py

POWER_KEYWORDS = [
    "power update",
    "scheduled power interruption",
    "power interruption",
    "power advisory",
    "power outage",
    "scheduled interruption"
]

def is_power_related(message: str) -> bool:
    if not message:
        return False

    text = message.lower().strip()

    for keyword in POWER_KEYWORDS:
        if text.startswith(keyword):
            return True

    return False
