import subprocess
from actions.journal import append
from actions.distro import pkg_manager

BASELINE = [
    "apt-transport-https",
    "sudo",
    "gnupg",
    "curl",
    "wget",
    "vim",
    "lsb-release",
    "mc",
    "htop",
    "tftp",
    "git",
    "tmux",
    "net-tools",
    "iproute2",
    "tcpdump",
    "nmap",
    "dnsutils",
    "msmtp",
]


def _installed_apt(pkg: str) -> bool:
    r = subprocess.run(
        ["dpkg-query", "-W", "-f=${Status}", pkg],
        capture_output=True, text=True
    )
    return "install ok installed" in r.stdout


def _installed_dnf(pkg: str) -> bool:
    return subprocess.run(["rpm", "-q", pkg], capture_output=True).returncode == 0


def install_baseline(distro: dict) -> bool:
    mgr = pkg_manager(distro)
    check = _installed_apt if mgr == "apt" else _installed_dnf
    missing = [p for p in BASELINE if not check(p)]
    if not missing:
        return False
    if mgr == "apt":
        subprocess.run(["apt-get", "update", "-q"], capture_output=True)
        subprocess.run(["apt-get", "install", "-y"] + missing, check=True)
    else:
        subprocess.run(["dnf", "install", "-y"] + missing, check=True)
    append("INSTALL", ", ".join(missing))
    return True


def install_package(name: str, distro: dict | None = None) -> None:
    mgr = pkg_manager(distro or {})
    cmd = ["apt-get", "install", "-y", name] if mgr == "apt" else ["dnf", "install", "-y", name]
    subprocess.run(cmd, check=True)
    append("INSTALL", name)
