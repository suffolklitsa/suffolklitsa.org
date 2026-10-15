"""Side-effect-free access to the LITSA field taxonomy (vendor/domains.py)."""

from __future__ import annotations

import ast
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "vendor" / "domains.py"


def _literal(name: str):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return ast.literal_eval(node.value)
    raise RuntimeError(f"Shared taxonomy does not define {name}")


FAMILIES = _literal("FAMILIES")
DOMAINS = [domain for _, _, domains in FAMILIES for domain in domains]
