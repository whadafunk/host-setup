#!/bin/bash
set -e

if ! command -v python3 &>/dev/null; then
    echo "python3 not found. Install it first."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 -m venv "$SCRIPT_DIR/.venv"
"$SCRIPT_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo "Done. Run the tool with:"
echo "  source .venv/bin/activate && python main.py"
