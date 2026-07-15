from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "src" / "astro_analysis_sdk" / "projection"
FORBIDDEN_PREFIXES = (
    "astro_analysis_sdk.pipelines",
    "astro_analysis_sdk.ephemeris",
    "swisseph",
    "pyswisseph",
)


def main() -> None:
    imports = {}
    violations = []
    for path in sorted(PACKAGE.rglob("*.py")):
        found = []
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                found.append(node.module or "")
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        imports[rel] = sorted(set(found))
        for name in found:
            if any(name == prefix or name.startswith(prefix + ".") for prefix in FORBIDDEN_PREFIXES):
                violations.append({"file": rel, "import": name})
    print(json.dumps({
        "projection_python_file_count": len(imports),
        "forbidden_import_count": len(violations),
        "forbidden_imports": violations,
        "imports": imports,
    }, indent=2))


if __name__ == "__main__":
    main()
