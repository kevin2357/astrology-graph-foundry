from __future__ import annotations

import json
import logging
import logging.config
import os
from pathlib import Path
from typing import Any

_DEFAULT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"}
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "astrology_graph_foundry.log",
            "mode": "a",
            "encoding": "utf-8",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "standard",
            "stream": "ext://sys.stderr",
        },
    },
    "root": {"level": "DEBUG", "handlers": ["file", "console"]},
}


def _candidate_config_paths(explicit_path: str | Path | None = None) -> list[Path]:
    paths: list[Path] = []
    if explicit_path:
        paths.append(Path(explicit_path))
    env_path = os.environ.get("ASTROLOGY_FOUNDRY_LOG_CONFIG")
    if env_path:
        paths.append(Path(env_path))
    paths.append(Path.cwd() / "logging.json")
    # package root when running from an editable src layout: src/astrology_graph_foundry/common -> repo root is parents[3]
    try:
        paths.append(Path(__file__).resolve().parents[3] / "logging.json")
    except IndexError:
        pass
    return paths


def configure_logging(config_path: str | Path | None = None, *, default_log_file: str = "astrology_graph_foundry.log") -> Path | None:
    """Configure Astrology Graph Foundry logging once.

    Search order:
    1. explicit `config_path`
    2. `ASTROLOGY_FOUNDRY_LOG_CONFIG`
    3. `./logging.json`
    4. repository/package-root `logging.json`

    If no file is found, a DEBUG-level file logger is installed in the current working directory.
    Returns the config path used, or None when the built-in fallback was used.
    """
    if getattr(configure_logging, "_configured", False):
        return getattr(configure_logging, "_config_path_used", None)

    for path in _candidate_config_paths(config_path):
        if path and path.exists():
            with path.open("r", encoding="utf-8") as f:
                config: dict[str, Any] = json.load(f)
            logging.config.dictConfig(config)
            configure_logging._configured = True
            configure_logging._config_path_used = path
            logging.getLogger(__name__).debug("Configured logging from %s", path)
            return path

    fallback = dict(_DEFAULT_CONFIG)
    fallback["handlers"] = dict(_DEFAULT_CONFIG["handlers"])
    fallback["handlers"]["file"] = dict(_DEFAULT_CONFIG["handlers"]["file"])
    fallback["handlers"]["file"]["filename"] = default_log_file
    logging.config.dictConfig(fallback)
    configure_logging._configured = True
    configure_logging._config_path_used = None
    logging.getLogger(__name__).debug("Configured logging from built-in fallback; file=%s", default_log_file)
    return None
