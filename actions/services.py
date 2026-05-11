import subprocess
from actions.journal import append

DISABLE_LIST = [
    "cups.path",
    "cups.service",
    "cups.socket",
    "cups-browsed.service",
    "avahi-daemon.service",
    "avahi-daemon.socket",
    "bluetooth.service",
    "ModemManager.service",
    "apparmor.service",
    "low-memory-monitor.service",
    "upower.service",
    "power-profiles-daemon.service",
    "colord.service",
    "switcheroo-control.service",
    "wpa_supplicant.service",
]

FIREWALL_SERVICES = [
    "ufw.service",
    "firewalld.service",
    "nftables.service",
]


def _unit_exists(name: str) -> bool:
    r = subprocess.run(
        ["systemctl", "list-unit-files", name],
        capture_output=True, text=True
    )
    return name in r.stdout


def _is_active_or_enabled(name: str) -> bool:
    for check in [["systemctl", "is-active", name], ["systemctl", "is-enabled", name]]:
        r = subprocess.run(check, capture_output=True, text=True)
        if r.stdout.strip() in ("active", "enabled", "static"):
            return True
    return False


def _disable_unit(name: str) -> bool:
    if not _unit_exists(name) or not _is_active_or_enabled(name):
        return False
    subprocess.run(["systemctl", "stop",    name], capture_output=True)
    subprocess.run(["systemctl", "disable", name], capture_output=True)
    subprocess.run(["systemctl", "mask",    name], capture_output=True)
    return True


def disable_all() -> bool:
    disabled = [svc for svc in DISABLE_LIST if _disable_unit(svc)]
    if disabled:
        append("SETUP", f"Disabled: {', '.join(disabled)}")
    return bool(disabled)


def disable_firewalls() -> bool:
    disabled = [svc for svc in FIREWALL_SERVICES if _disable_unit(svc)]
    if disabled:
        append("SETUP", f"Disabled firewall services: {', '.join(disabled)}")
    return bool(disabled)


def set_multi_user_target() -> bool:
    r = subprocess.run(["systemctl", "get-default"], capture_output=True, text=True)
    if r.stdout.strip() == "multi-user.target":
        return False
    subprocess.run(["systemctl", "set-default", "multi-user.target"], check=True)
    append("SETUP", "Set default target to multi-user.target")
    return True
