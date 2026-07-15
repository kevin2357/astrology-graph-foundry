from __future__ import annotations
import gzip
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    logger.debug("Reading JSONL: %s", path)
    rows=[]
    with Path(path).open("r", encoding="utf-8") as f:
        for line_no,line in enumerate(f,1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Could not decode JSON in {path} line {line_no}: {exc}") from exc
    logger.debug("Read %d JSONL rows from %s", len(rows), path)
    return rows

def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    logger.info("Writing %d JSONL rows to %s", len(rows), path)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")

def write_json(path: str | Path, data: Any) -> None:
    logger.info("Writing JSON to %s", path)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    if path.suffix == ".gz":
        with path.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                compressed.write(payload.encode("utf-8"))
        return
    path.write_text(payload, encoding="utf-8")

def read_json(path: str | Path) -> Any:
    logger.debug("Reading JSON: %s", path)
    path = Path(path)
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding="utf-8"))

def clean_body_name(name: object) -> str:
    s=str(name)
    return s[1:] if s.startswith("n") else s

def load_person(path: str | Path) -> dict[str, Any]:
    logger.info("Loading person ephemeris JSONL: %s", path)
    rows=read_jsonl(path)
    metadata=next((r for r in rows if r.get("type")=="person_metadata"), None)
    natal=next((r for r in rows if r.get("type")=="natal_chart"), None)
    daily=[r for r in rows if r.get("type")=="person_daily_snapshot"]
    if metadata is None or natal is None:
        raise ValueError(f"{path} must contain person_metadata and natal_chart records")
    logger.info("Loaded person=%s with %d daily snapshots", metadata.get("person"), len(daily))
    return {"path": str(path), "metadata": metadata, "natal": natal, "daily": daily, "rows": rows}

def load_global(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    rows=read_jsonl(path)
    metadata=next((r for r in rows if r.get("type")=="global_metadata"), None)
    daily=[r for r in rows if r.get("type")=="global_daily_snapshot"]
    return {"path": str(path), "metadata": metadata, "daily": daily, "rows": rows}

def load_natal_dataset(path: str | Path) -> dict[str, Any]:
    logger.info("Loading natal dataset: %s", path)
    data=read_json(path)
    if "natal" not in data:
        raise ValueError(f"{path} is missing `natal`")
    return data
