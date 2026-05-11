import re
import subprocess
from pathlib import Path
from actions.journal import append
from actions import grub

SSHD_CONFIG = Path("/etc/ssh/sshd_config")


def disable_apparmor() -> bool:
    changed_grub = grub.add_cmdline_param("apparmor=0")
    grub.add_cmdline_param("security=")

    r = subprocess.run(["systemctl", "is-enabled", "apparmor"], capture_output=True, text=True)
    changed_svc = False
    if r.stdout.strip() not in ("disabled", "masked", "not-found", ""):
        subprocess.run(["systemctl", "stop",    "apparmor"], capture_output=True)
        subprocess.run(["systemctl", "disable", "apparmor"], capture_output=True)
        subprocess.run(["systemctl", "mask",    "apparmor"], capture_output=True)
        changed_svc = True

    changed = changed_grub or changed_svc
    if changed:
        append("SETUP", "Disabled AppArmor (GRUB + systemd)")
    return changed


def _set_sshd_option(key: str, value: str) -> bool:
    if not SSHD_CONFIG.exists():
        return False
    content = SSHD_CONFIG.read_text()
    if re.search(rf"^{re.escape(key)}\s+{re.escape(value)}\s*$", content, re.MULTILINE):
        return False
    new_line = f"{key} {value}"
    pattern = re.compile(rf"^#?\s*{re.escape(key)}\s+.*", re.MULTILINE)
    if pattern.search(content):
        content = pattern.sub(new_line, content, count=1)
    else:
        content = content.rstrip() + f"\n{new_line}\n"
    SSHD_CONFIG.write_text(content)
    return True


def harden_ssh() -> bool:
    changes = []
    for key, value in [
        ("PermitRootLogin",      "no"),
        ("PasswordAuthentication", "no"),
        ("ClientAliveInterval",  "300"),
        ("ClientAliveCountMax",  "2"),
    ]:
        if _set_sshd_option(key, value):
            changes.append(f"{key} {value}")
    if not changes:
        return False
    subprocess.run(["systemctl", "restart", "sshd"], capture_output=True)
    append("SETUP", f"Hardened SSH: {', '.join(changes)}")
    return True
