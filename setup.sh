#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 &>/dev/null; then
    echo "python3 not found. Install it first."
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

# On Debian/Ubuntu, venv and pip are separate packages
if command -v apt-get &>/dev/null; then
    MISSING=()
    python3 -m ensurepip --version &>/dev/null || MISSING+=("python${PY_VER}-venv")
    dpkg -s "python${PY_VER}-venv" &>/dev/null || MISSING+=("python${PY_VER}-venv")
    if [ ${#MISSING[@]} -gt 0 ]; then
        echo "Installing missing packages: ${MISSING[*]}"
        apt-get install -y "${MISSING[@]}"
    fi
fi

python3 -m venv "$SCRIPT_DIR/.venv"
"$SCRIPT_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo "Done. Run the tool with:"
echo "  source .venv/bin/activate && python main.py"
