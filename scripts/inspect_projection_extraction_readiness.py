from __future__ import annotations
import importlib.util, json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
projection_dir=root / "src" / "astrology_graph_foundry" / "projection"
result={
  "inspection":"chunk2.8_external_projection_integration",
  "embedded_projection_package_present": projection_dir.exists(),
  "semantic_projection_importable": importlib.util.find_spec("semantic_projection") is not None,
  "adapter_present": (root / "src" / "astrology_graph_foundry" / "projection_adapter.py").exists(),
  "ready": (not projection_dir.exists()) and importlib.util.find_spec("semantic_projection") is not None,
  "ownership": {
    "astrology_graph_foundry":["canonical astrology graph","structural evidence","saved-package adapter","CLI bridge"],
    "semantic_projection_core":["projection contracts","engine","profiles","audit","diagnostics","materialization","term registries","rendering"]
  }
}
print(json.dumps(result,indent=2))
