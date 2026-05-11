#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 &>/dev/null; then
    echo "python3 not found. Install it first."
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

if command -v apt-get &>/dev/null; then
    MISSING=()
    dpkg -s "python3-pip" &>/dev/null      || MISSING+=("python3-pip")
    dpkg -s "python${PY_VER}-venv" &>/dev/null || MISSING+=("python${PY_VER}-venv")
    if [ ${#MISSING[@]} -gt 0 ]; then
        echo "Installing: ${MISSING[*]}"
        apt-get install -y "${MISSING[@]}"
    fi
fi

pip3 install --break-system-packages -r "$SCRIPT_DIR/requirements.txt"

echo "Done. Run the tool with:"
echo "  sudo python3 main.py"
