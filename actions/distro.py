from pathlib import Path


def detect() -> dict:
    for path in [Path("/etc/os-release"), Path("/usr/lib/os-release")]:
        if path.exists():
            info = {}
            for line in path.read_text().splitlines():
                if "=" in line:
                    k, _, v = line.partition("=")
                    info[k.strip()] = v.strip().strip('"')
            return info
    return {}


def pkg_manager(distro: dict) -> str:
    distro_id = distro.get("ID", "").lower()
    like = distro.get("ID_LIKE", "").lower()
    if any(x in f"{distro_id} {like}" for x in ("debian", "ubuntu")):
        return "apt"
    if any(x in f"{distro_id} {like}" for x in ("fedora", "rhel", "centos", "rocky", "alma")):
        return "dnf"
    return "apt"
