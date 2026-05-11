import socket
import subprocess
from datetime import date
from pathlib import Path
from actions.journal import append

TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "motd.txt"
MOTD_PATH = Path("/etc/motd")


def _run(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def _interfaces() -> str:
    raw = _run("ip -o addr show | awk '{print $2, $3, $4}'")
    lines = [f"    {line}" for line in raw.splitlines() if line]
    return "\n".join(lines)


def _disk() -> str:
    raw = _run("df -h --output=source,size,used,avail,pcent,target -x tmpfs -x devtmpfs | tail -n +2")
    lines = [f"    {line}" for line in raw.splitlines() if line]
    return "\n".join(lines)


def _network() -> dict:
    ip = _run("ip route get 1 | awk '{print $7}' | head -1")
    gw = _run("ip route | awk '/default/{print $3}' | head -1")
    dns = _run("resolvectl status 2>/dev/null | awk '/DNS Servers/{print $3}' | head -1")
    if not dns:
        dns = _run("awk '/^nameserver/{print $2; exit}' /etc/resolv.conf")
    domain = _run("hostname -d 2>/dev/null || dnsdomainname 2>/dev/null || echo ''")
    return {"ip": ip, "gw": gw, "dns": dns, "domain": domain}


def update(context: dict | None = None) -> None:
    template = TEMPLATE_PATH.read_text()
    net = _network()

    defaults: dict = {
        "LAST_UPDATE": date.today().strftime("%d/%m/%Y"),
        "HOSTNAME": socket.getfqdn(),
        "ASSET_NR": "N/A",
        "BUSINESS_OWNER": "N/A",
        "TECHNICAL_OWNER": "N/A",
        "LOCATION": "N/A",
        "DESCRIPTION": "N/A",
        "SERVICES": "    N/A",
        "USAGE": "    N/A",
        "ACTIVE_USERS": "    N/A",
        "NET_IP": net["ip"],
        "NET_GW": net["gw"],
        "NET_DNS": net["dns"],
        "NET_DOMAIN": net["domain"],
        "INTERFACES": _interfaces(),
        "DISK": _disk(),
    }

    if context:
        defaults.update(context)

    MOTD_PATH.write_text(template.format(**defaults))
    append("SETUP", "Updated /etc/motd")
