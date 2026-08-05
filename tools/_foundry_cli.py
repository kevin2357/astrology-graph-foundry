"""Shared support for human-friendly Astrology Graph Foundry tools."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

ALLOW_PROMPTS = True


def configure_execution(args: Any) -> None:
    global ALLOW_PROMPTS
    ALLOW_PROMPTS = not bool(getattr(args, "non_interactive", False))


def required(label: str, value: Any = None) -> str:
    if value is not None and str(value).strip():
        return str(value)
    if not ALLOW_PROMPTS or not sys.stdin.isatty():
        raise ValueError(f"{label} is required for unattended execution")
    answer = input(f"{label}: ").strip()
    if not answer:
        raise ValueError(f"{label} is required")
    return answer


def choose(label: str, choices: Iterable[tuple[str, str]], value: str | None = None) -> str:
    rows = list(choices)
    keys = {key for key, _ in rows}
    if value is not None:
        if value not in keys:
            raise ValueError(f"Invalid {label.lower()} {value!r}; choose from {sorted(keys)}")
        return value
    if not ALLOW_PROMPTS or not sys.stdin.isatty():
        raise ValueError(f"{label} is required for unattended execution")
    print(label + ":")
    for index, (key, description) in enumerate(rows, 1):
        print(f"  {index}. {description} ({key})")
    answer = input("Selection: ").strip()
    if answer.isdigit() and 1 <= int(answer) <= len(rows):
        return rows[int(answer) - 1][0]
    if answer in keys:
        return answer
    raise ValueError(f"Invalid selection {answer!r}")


def existing_file(label: str, value: Any = None) -> str:
    path = Path(required(label, value)).expanduser()
    if not path.is_file():
        raise ValueError(f"{label} does not exist or is not a file: {path}")
    return str(path)


def output_dir(value: Any = None) -> Path:
    path = Path(required("Output directory", value)).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def add_common_execution_arguments(parser: Any) -> None:
    parser.add_argument("--dry-run", action="store_true", help="Print delegated commands without executing them.")
    parser.add_argument("--non-interactive", action="store_true", help="Never prompt; fail if a required value is missing.")


def option(command: list[str], flag: str, value: Any) -> None:
    if value is not None and str(value) != "":
        command.extend([flag, str(value)])


def flag(command: list[str], name: str, enabled: bool) -> None:
    if enabled:
        command.append(name)


def cli_command(subcommand: str) -> list[str]:
    return [sys.executable, "-m", "astrology_graph_foundry.cli", subcommand]


def display_command(command: list[str]) -> str:
    if sys.platform == "win32":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def run_commands(commands: list[list[str]], *, dry_run: bool = False) -> None:
    for command in commands:
        print(f"Delegating: {display_command(command)}")
        if not dry_run:
            subprocess.run(command, cwd=REPO_ROOT, check=True)


def print_outputs(paths: Iterable[Path], *, dry_run: bool) -> None:
    label = "Would write" if dry_run else "Wrote"
    for path in paths:
        print(f"{label}: {path}")


def print_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def run_main(callback: Callable[[], int]) -> int:
    try:
        return callback()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.", file=sys.stderr)
        return 130
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: delegated Foundry command failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode or 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def append_live_birth_arguments(command: list[str], args: Any, prefix: str = "") -> None:
    cli_prefix = f"--{prefix}-" if prefix else "--"
    attr_prefix = f"{prefix.replace('-', '_')}_" if prefix else ""
    fields = (
        ("name", "name"),
        ("birth-local", "birth_local"),
        ("birth-timezone", "birth_timezone"),
        ("birth-lat", "birth_lat"),
        ("birth-lon", "birth_lon"),
        ("birth-location-label", "birth_location_label"),
        ("source-chart-id", "source_chart_id"),
    )
    required_fields = {"name", "birth_local", "birth_timezone", "birth_lat", "birth_lon"}
    for flag_name, attr_name in fields:
        value = getattr(args, attr_prefix + attr_name)
        if attr_name in required_fields:
            value = required(f"{prefix or 'person'} {flag_name.replace('-', ' ')}", value)
        option(command, cli_prefix + flag_name, value)
