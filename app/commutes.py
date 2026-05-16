import json
import logging
from pathlib import Path

logger = logging.getLogger("chimuter.commutes")

_catalog: list[dict] = []


def load_commutes(path: Path | None = None):
    global _catalog
    if path is None:
        path = Path(__file__).parent.parent / "commutes.json"
    if not path.exists():
        logger.error("commutes.json not found at %s", path)
        _catalog = []
        return
    with open(path) as f:
        _catalog = json.load(f)
    logger.info("Loaded %d commute(s) from catalog", len(_catalog))


def get_all_commutes() -> list[dict]:
    return _catalog


def get_commute(commute_id: str) -> dict | None:
    for c in _catalog:
        if c["id"] == commute_id:
            return c
    return None
