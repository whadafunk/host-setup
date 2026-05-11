import subprocess
from pathlib import Path
from actions.journal import append

ADMIN_USER = "admin"
ADMIN_HOME = Path("/home/admin")


def _user_exists(name: str) -> bool:
    return subprocess.run(["id", name], capture_output=True).returncode == 0


def create_admin(pubkey_dir: Path) -> bool:
    if _user_exists(ADMIN_USER):
        return False

    subprocess.run([
        "useradd",
        "-c", "generic admin",
        "-s", "/bin/bash",
        "-g", "root",
        "-G", "sudo,users",
        "-d", str(ADMIN_HOME),
        "-m", ADMIN_USER,
    ], check=True)

    ssh_dir = ADMIN_HOME / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    authorized = ssh_dir / "authorized_keys"

    keys_dir = pubkey_dir / "keys" if (pubkey_dir / "keys").exists() else pubkey_dir
    keys_added = []
    for key_file in sorted(keys_dir.glob("*.pub")):
        key_content = key_file.read_text().strip()
        with authorized.open("a") as f:
            f.write(key_content + "\n")
        keys_added.append(key_file.name)

    authorized.chmod(0o600)
    subprocess.run(["chown", "-R", f"{ADMIN_USER}:root", str(ssh_dir)], check=True)

    append("SETUP", f"Created user '{ADMIN_USER}' with keys: {', '.join(keys_added)}")
    return True
