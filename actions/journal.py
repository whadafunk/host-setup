import os
from datetime import datetime

JOURNAL_PATH = "/var/log/host-journal.md"


def append(category: str, message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {timestamp}\n**[{category.upper()}]** {message}\n"
    os.makedirs(os.path.dirname(JOURNAL_PATH), exist_ok=True)
    with open(JOURNAL_PATH, "a") as f:
        f.write(entry)
