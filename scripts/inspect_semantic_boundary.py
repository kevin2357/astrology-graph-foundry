from __future__ import annotations
import json, sys
from pathlib import Path

LEGACY_SEMANTIC_ALIAS_FIELDS = (
    "semantic_graph", "theme_metrics", "relationship_metrics",
    "evidence_graph", "report_materials",
)

_ALLOWED_NAMESPACE_KEYS = {
    "projection_views",
    "projection_view_summaries",
    "orthodox_projection_extract",
    "orthodox_relationship_metric_summary",
}

def count_legacy_aliases(value, *, path=()):
    """Count legacy aliases only in forbidden materialization locations."""
    if isinstance(value, list):
        return sum(
            count_legacy_aliases(item, path=path + ("[]",))
            for item in value
        )
    if not isinstance(value, dict):
        return 0

    # Explicit projection namespaces are modern homes for these field names.
    if any(part in _ALLOWED_NAMESPACE_KEYS for part in path):
        return 0

    count = 0
    for field in LEGACY_SEMANTIC_ALIAS_FIELDS:
        if field in value:
            count += 1

    for key, child in value.items():
        count += count_legacy_aliases(child, path=path + (str(key),))
    return count

def read(path): return json.loads(Path(path).read_text(encoding="utf-8"))

def audit_graph(graph):
    rows = list(graph.get("objects") or []) + list(graph.get("relationships") or [])
    nested = graph.get("nested_canonical_graph_registry") or {}
    nested_audits = [audit_graph(g) for g in nested.values() if isinstance(g, dict)]
    return {
        "graphs": 1 + sum(a["graphs"] for a in nested_audits),
        "objects": len(graph.get("objects") or []) + sum(a["objects"] for a in nested_audits),
        "relationships": len(graph.get("relationships") or []) + sum(a["relationships"] for a in nested_audits),
        "theme_leaks": sum(1 for r in rows if "theme_tags" in r or "orthodox_astrology_theme_tags" in r) + sum(a["theme_leaks"] for a in nested_audits),
        "missing_evidence": sum(1 for r in rows if not r.get("evidence_metadata")) + sum(a["missing_evidence"] for a in nested_audits),
        "missing_strength": sum(1 for r in rows if r.get("structural_strength_score") is None) + sum(a["missing_strength"] for a in nested_audits),
        "missing_sensor": sum(1 for r in rows if not (r.get("evidence_metadata") or {}).get("sensor_instance_id")) + sum(a["missing_sensor"] for a in nested_audits),
        "missing_source_ids": sum(1 for r in rows if not (r.get("evidence_metadata") or {}).get("source_chart_ids")) + sum(a["missing_source_ids"] for a in nested_audits),
        "nested_count": len(nested) + sum(a["nested_count"] for a in nested_audits),
    }

def inspect(path):
    p = Path(path); d = read(p)
    c = d.get("canonical_astrology_graph") or {}
    cs = d.get("canonical_astrology_graph_summary") or {}
    s = d.get("structural_evidence_graph") or {}
    ss = d.get("structural_evidence_summary") or {}
    o = (d.get("projection_views") or {}).get("orthodox_astrology.v1") or {}
    osum = (d.get("projection_view_summaries") or {}).get("orthodox_astrology.v1") or {}
    m = d.get("metadata") or {}; b = d.get("semantic_boundary") or {}
    if c:
        mode="full"; a=audit_graph(c)
        objects=len(c.get("objects") or []); rels=len(c.get("relationships") or [])
    elif cs:
        mode="summary"; objects=int(cs.get("object_count") or 0); rels=int(cs.get("relationship_count") or 0)
        a={"graphs":0,"objects":objects,"relationships":rels,"theme_leaks":None,"missing_evidence":None,"missing_strength":None,"missing_sensor":None,"missing_source_ids":None,"nested_count":int(cs.get("nested_canonical_graph_count") or 0)}
    else:
        mode="absent"; objects=rels=0
        a={"graphs":0,"objects":0,"relationships":0,"theme_leaks":None,"missing_evidence":None,"missing_strength":None,"missing_sensor":None,"missing_source_ids":None,"nested_count":0}
    return {
        "file":str(p),"analysis_type":m.get("analysis_type"),"view_type":d.get("view_type") or m.get("view_type"),
        "canonical_materialization":mode,"canonical_objects":objects,"canonical_relationships":rels,
        "recursive_canonical_graph_count":a["graphs"],"recursive_canonical_objects":a["objects"],"recursive_canonical_relationships":a["relationships"],
        "nested_canonical_graph_count":a["nested_count"],"canonical_theme_leaks":a["theme_leaks"],
        "canonical_rows_missing_evidence_metadata":a["missing_evidence"],"canonical_rows_missing_structural_strength":a["missing_strength"],
        "canonical_rows_missing_sensor_instance_id":a["missing_sensor"],"canonical_rows_missing_source_chart_ids":a["missing_source_ids"],
        "source_chart_id":m.get("source_chart_id") or b.get("source_chart_id") or c.get("source_chart_id") or cs.get("source_chart_id"),
        "source_chart_ids":m.get("source_chart_ids") or b.get("source_chart_ids") or c.get("source_chart_ids") or cs.get("source_chart_ids") or [],
        "sensor_instance_id":m.get("sensor_instance_id") or b.get("sensor_instance_id") or c.get("sensor_instance_id") or cs.get("sensor_instance_id"),
        "record_independence_group_count":s.get("record_independence_group_count") if s else ss.get("record_independence_group_count"),
        "evidence_family_group_count":s.get("evidence_family_group_count") if s else ss.get("evidence_family_group_count"),
        "source_chart_family_group_count":s.get("source_chart_family_group_count") if s else ss.get("source_chart_family_group_count"),
        "orthodox_theme_metric_count":len(o.get("theme_metrics") or []) if o else int(osum.get("theme_metric_count") or 0),
        "orthodox_claim_candidate_count":len(o.get("claim_candidates") or []) if o else int(osum.get("claim_candidate_count") or 0),
        "orthodox_metric_source_field":o.get("metric_source_field") if o else osum.get("metric_source_field"),
        "materialization_policy":m.get("materialization_policy") or b.get("materialization_policy"),
        "legacy_semantic_alias_count":count_legacy_aliases(d),
        "has_boundary":bool(b),"size_bytes":p.stat().st_size,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("Usage: python scripts/inspect_semantic_boundary.py <json-file-or-directory>")
    src=Path(sys.argv[1]); paths=[src] if src.is_file() else sorted(src.rglob("*.json"))
    rows=[]
    for p in paths:
        try: d=read(p)
        except Exception: continue
        if "semantic_boundary" in d: rows.append(inspect(p))
    full=[r for r in rows if r["canonical_materialization"]=="full"]
    compact=[r for r in rows if r["canonical_materialization"]=="summary"]
    identities={}
    collisions={}
    for r in rows:
        sid=r.get("sensor_instance_id")
        if not sid: continue
        key=(r.get("analysis_type"),tuple(r.get("source_chart_ids") or []))
        if sid in identities and identities[sid]!=key: collisions.setdefault(sid,[]).append(r["file"])
        identities.setdefault(sid,key)
    print(json.dumps({
        "package_count":len(rows),"full_canonical_package_count":len(full),"summary_canonical_view_count":len(compact),
        "absent_canonical_boundary_count":sum(r["canonical_materialization"]=="absent" for r in rows),
        "all_materialized_canonical_graphs_theme_clean":all(r["canonical_theme_leaks"]==0 for r in full),
        "all_materialized_canonical_rows_have_evidence_metadata":all(r["canonical_rows_missing_evidence_metadata"]==0 for r in full),
        "all_materialized_canonical_rows_have_structural_strength":all(r["canonical_rows_missing_structural_strength"]==0 for r in full),
        "all_materialized_canonical_rows_have_sensor_instance_id":all(r["canonical_rows_missing_sensor_instance_id"]==0 for r in full),
        "all_materialized_canonical_rows_have_source_chart_ids":all(r["canonical_rows_missing_source_chart_ids"]==0 for r in full),
        "all_packages_expose_sensor_instance_id":all(bool(r.get("sensor_instance_id")) for r in rows),
        "all_packages_expose_source_chart_ids":all(bool(r.get("source_chart_ids")) for r in rows),
        "all_packages_use_named_materialization_policy":all(bool(r.get("materialization_policy")) for r in rows),
        "all_legacy_semantic_aliases_removed":all(r.get("legacy_semantic_alias_count")==0 for r in rows),
        "all_full_packages_materialize_canonical_boundary":all(
            r["canonical_materialization"]=="full"
            for r in rows
            if not r.get("view_type")
        ),
        "sensor_instance_collision_count":len(collisions),"sensor_instance_collisions":collisions,"packages":rows
    },indent=2))
if __name__=="__main__": main()
