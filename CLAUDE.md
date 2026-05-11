# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

`host-setup` is a Python CLI tool for configuring newly installed Linux systems. It provides a TUI wizard for applying baseline configuration actions, a system journal for tracking changes, and a package install wrapper that auto-journals.

## Running the tool

```bash
# Install dependencies
pip install -r requirements.txt

# Run the TUI setup wizard
python main.py apply

# Manual journal entry
python main.py journal add "note"

# View journal
python main.py journal view

# Install a package and auto-journal it
python main.py install <package>

# Re-render MOTD from template
python main.py motd update
```

## Tech stack

- **Typer** — CLI framework, subcommands defined in `main.py`
- **questionary** — interactive TUI checkbox menu for selecting actions before applying
- **rich** — terminal output formatting and journal pagination

## Architecture

`main.py` is the entry point and wires together Typer subcommands. Each subcommand delegates to a module in `actions/`.

```
main.py          # CLI entry point, Typer app, subcommand registration
actions/
  services.py    # disable/enable systemd services (bluetooth, cups, avahi, etc.)
  network.py     # disable IPv6, network tweaks
  security.py    # AppArmor / SELinux configuration
  packages.py    # baseline package installation
  motd.py        # render MOTD template to /etc/motd
  journal.py     # append-only markdown journal at /var/log/host-journal.md
templates/
  motd.txt       # MOTD template (user-editable)
```

## Key conventions

**Actions are idempotent** — every function in `actions/` checks current state before changing it. For example, disabling a service first checks if it is already disabled.

**Everything the wizard applies is auto-journaled** — `actions/journal.py` exposes an `append(category, message)` function. Every action module calls it after a successful change. Journal entries are appended as markdown with a timestamp header.

**Journal format** — append-only markdown at `/var/log/host-journal.md`:
```
## 2026-05-11 14:32
**[SETUP]** Disabled IPv6, disabled bluetooth service

**[INSTALL]** nginx

**[NOTE]** Configured nginx reverse proxy for port 3000
```

**TUI flow** — `apply` subcommand presents a `questionary.checkbox` menu of all available actions grouped by category. The user selects with spacebar, confirms with Enter, then actions run sequentially with `rich` progress output.

**Privilege requirement** — most actions require root. Check `os.geteuid() == 0` at startup in `main.py` and exit early with a clear message if not root.
