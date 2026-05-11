import re
import subprocess
from pathlib import Path
from actions.journal import append
from actions import grub

SYSCTL_CONF = Path("/etc/sysctl.d/99-host-setup.conf")


def _sysctl_get(key: str) -> str:
    r = subprocess.run(["sysctl", "-n", key], capture_output=True, text=True)
    return r.stdout.strip()


def _set_sysctl(key: str, value: str) -> bool:
    existing = SYSCTL_CONF.read_text() if SYSCTL_CONF.exists() else ""
    new_line = f"{key}={value}"
    if re.search(rf"^{re.escape(key)}={re.escape(value)}\s*$", existing, re.MULTILINE):
        return False
    if re.search(rf"^{re.escape(key)}=", existing, re.MULTILINE):
        new_content = re.sub(rf"^{re.escape(key)}=.*$", new_line, existing, flags=re.MULTILINE)
    else:
        new_content = existing.rstrip() + "\n" + new_line + "\n"
    SYSCTL_CONF.write_text(new_content)
    subprocess.run(["sysctl", "-p", str(SYSCTL_CONF)], capture_output=True)
    return True


def disable_ipv6() -> bool:
    changed_grub = grub.add_cmdline_param("ipv6.disable=1")
    params = [
        ("net.ipv6.conf.all.disable_ipv6",     "1"),
        ("net.ipv6.conf.default.disable_ipv6", "1"),
        ("net.ipv6.conf.lo.disable_ipv6",      "1"),
    ]
    changed_sysctl = any(_set_sysctl(k, v) for k, v in params)
    changed = changed_grub or changed_sysctl
    if changed:
        append("SETUP", "Disabled IPv6 (GRUB + sysctl)")
    return changed


def toggle_syn_cookies() -> bool:
    current = _sysctl_get("net.ipv4.tcp_syncookies")
    new_val = "0" if current == "1" else "1"
    _set_sysctl("net.ipv4.tcp_syncookies", new_val)
    action = "Disabled" if new_val == "0" else "Enabled"
    append("SETUP", f"{action} TCP SYN cookies")
    return True
