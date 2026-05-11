import os
from collections import namedtuple
from pathlib import Path

import questionary
import typer
from questionary import Choice, Separator
from rich.console import Console
from rich.rule import Rule

from actions import journal, motd, network, packages, security, services, users
from actions.distro import detect as detect_distro

app = typer.Typer(help="Host setup wizard", invoke_without_command=True)
console = Console()

PUBKEY_DIR = Path(__file__).parent

Action = namedtuple("Action", ["category", "label", "fn"])


def _require_root() -> None:
    if os.geteuid() != 0:
        console.print("[bold red]Error:[/] this command must be run as root.")
        raise SystemExit(1)


def _build_actions(distro: dict) -> list:
    return [
        Separator("── Services ──────────────────────────"),
        Choice("Disable unnecessary services",      value=Action("services", "Disable unnecessary services",      services.disable_all)),
        Choice("Disable firewall services",         value=Action("services", "Disable firewall services",         services.disable_firewalls)),
        Choice("Set default target: multi-user",    value=Action("services", "Set default target: multi-user",    services.set_multi_user_target)),
        Separator("── Network ───────────────────────────"),
        Choice("Disable IPv6 (GRUB + sysctl)",      value=Action("network",  "Disable IPv6 (GRUB + sysctl)",      network.disable_ipv6)),
        Choice("Toggle TCP SYN cookies",            value=Action("network",  "Toggle TCP SYN cookies",            network.toggle_syn_cookies)),
        Separator("── Security ──────────────────────────"),
        Choice("Disable AppArmor (GRUB + systemd)", value=Action("security", "Disable AppArmor (GRUB + systemd)", security.disable_apparmor)),
        Choice("Harden SSH config",                 value=Action("security", "Harden SSH config",                 security.harden_ssh)),
        Separator("── Packages ──────────────────────────"),
        Choice("Install baseline packages",         value=Action("packages", "Install baseline packages",         lambda: packages.install_baseline(distro))),
        Separator("── Users ─────────────────────────────"),
        Choice("Create admin user + copy pubkeys",  value=Action("users",    "Create admin user + copy pubkeys",  lambda: users.create_admin(PUBKEY_DIR))),
        Separator("── System ────────────────────────────"),
        Choice("Update MOTD",                       value=Action("system",   "Update MOTD",                       motd.update)),
    ]


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return

    distro = detect_distro()
    distro_name = distro.get("PRETTY_NAME", "Unknown Linux")
    console.print(f"\n[bold]Host Setup[/]  [dim]·[/]  [cyan]{distro_name}[/]\n")

    top = questionary.select(
        "What would you like to do?",
        choices=[
            Choice("Run optimizations", value="optimize"),
            Choice("Log in journal",    value="journal"),
            Choice("Exit",              value="exit"),
        ],
    ).ask()

    if top is None or top == "exit":
        raise SystemExit(0)

    if top == "journal":
        note = questionary.text("Journal note:").ask()
        if note and note.strip():
            journal.append("NOTE", note.strip())
            console.print("[green]Entry added.[/]")
        return

    selected = questionary.checkbox(
        "Select actions to apply:",
        choices=_build_actions(distro),
    ).ask()

    if not selected:
        console.print("No actions selected.")
        return

    mode = questionary.select(
        "How would you like to proceed?",
        choices=[
            Choice("Apply    — execute selected actions", value="apply"),
            Choice("Dry run  — preview what would change", value="dry"),
            Choice("Cancel",                               value="cancel"),
        ],
    ).ask()

    if mode is None or mode == "cancel":
        console.print("Cancelled.")
        return

    console.print()

    if mode == "dry":
        console.print(Rule("[yellow]Dry run — no changes will be made[/]"))
        for action in selected:
            console.print(f"  [yellow]~[/] {action.label}")
        console.print()
        console.print(Rule("[yellow]End of dry run[/]"))
        return

    _require_root()
    console.print(Rule("Applying"))

    for action in selected:
        console.print(f"  [cyan]→[/] {action.label}...", end=" ")
        try:
            changed = action.fn()
            console.print("[yellow]already done[/]" if changed is False else "[green]ok[/]")
        except Exception as e:
            console.print(f"[red]failed[/] — {e}")

    console.print()
    console.print(Rule("[green]Done[/]"))


@app.command()
def install(package: str = typer.Argument(..., help="Package name to install")) -> None:
    """Install a package and record it in the journal."""
    _require_root()
    distro = detect_distro()
    packages.install_package(package, distro)
    console.print(f"[green]Installed[/] {package}")


journal_app = typer.Typer(help="Manage the system journal")
app.add_typer(journal_app, name="journal")


@journal_app.command("add")
def journal_add(note: str = typer.Argument(..., help="Note to append")) -> None:
    """Append a manual note to the journal."""
    journal.append("NOTE", note)
    console.print("[green]Journal entry added.[/]")


@journal_app.command("view")
def journal_view() -> None:
    """Display the journal."""
    from rich.markdown import Markdown
    path = Path(journal.JOURNAL_PATH)
    if not path.exists():
        console.print("Journal is empty.")
        return
    console.print(Markdown(path.read_text()))


if __name__ == "__main__":
    app()
