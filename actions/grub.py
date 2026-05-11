import re
import subprocess
from pathlib import Path

GRUB_DEFAULT = Path("/etc/default/grub")


def _update_grub() -> None:
    for cmd in [["update-grub"], ["grub2-mkconfig", "-o", "/boot/grub2/grub.cfg"]]:
        if subprocess.run(cmd, capture_output=True).returncode == 0:
            return


def add_cmdline_param(param: str) -> bool:
    if not GRUB_DEFAULT.exists():
        return False
    lines = GRUB_DEFAULT.read_text().splitlines()
    changed = False
    result = []
    for line in lines:
        m = re.match(r'(GRUB_CMDLINE_LINUX=")([^"]*)"', line)
        if m and param not in m.group(2).split():
            line = f'{m.group(1)}{m.group(2).strip()} {param}"'
            changed = True
        result.append(line)
    if changed:
        GRUB_DEFAULT.write_text("\n".join(result) + "\n")
        _update_grub()
    return changed


def remove_cmdline_param(param: str) -> bool:
    if not GRUB_DEFAULT.exists():
        return False
    lines = GRUB_DEFAULT.read_text().splitlines()
    changed = False
    result = []
    for line in lines:
        m = re.match(r'(GRUB_CMDLINE_LINUX=")([^"]*)"', line)
        if m and param in m.group(2).split():
            params = [p for p in m.group(2).split() if p != param]
            line = f'{m.group(1)}{" ".join(params)}"'
            changed = True
        result.append(line)
    if changed:
        GRUB_DEFAULT.write_text("\n".join(result) + "\n")
        _update_grub()
    return changed
