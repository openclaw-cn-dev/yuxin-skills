"""Tool registry: rich tool definitions (JSON schema + execution handler) that
skills and the router can invoke dynamically.

Every tool is a pure, deterministic function wrapped in a ``Tool`` with an
explicit input/output schema. The registry validates arguments before
execution and converts exceptions into ``ToolError`` with a stable code, so
callers get structured, recoverable failures instead of stack traces.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .errors import ToolError
from . import chemistry, biofilter, diseases


@dataclass
class ToolContext:
    """Shared runtime context handed to every tool handler."""
    settings: Any = None
    species_registry: Any = None
    knowledge_base_text: str = ""
    logger: Any = None


@dataclass
class Tool:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any], ToolContext], Any]
    tags: List[str] = field(default_factory=list)

    def validate_input(self, args: Dict[str, Any]) -> None:
        required = self.input_schema.get("required", [])
        for key in required:
            if key not in args:
                raise ToolError(f"tool '{self.name}' missing required arg '{key}'")
        props = self.input_schema.get("properties", {})
        for key, val in args.items():
            if key in props:
                t = props[key].get("type")
                _check_type(key, val, t)

    def run(self, args: Dict[str, Any], ctx: ToolContext) -> Any:
        self.validate_input(args)
        try:
            return self.handler(args, ctx)
        except (ToolError, ValueError, TypeError) as exc:
            raise ToolError(f"tool '{self.name}' failed: {exc}", cause=exc) from exc


def _check_type(key: str, val: Any, t: Optional[Any]) -> None:
    if t is None or val is None:
        return
    mapping = {
        "number": (int, float),
        "integer": int,
        "string": str,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    expected = mapping.get(t)
    if expected and not isinstance(val, expected):
        raise ToolError(f"arg '{key}' expected type {t}, got {type(val).__name__}")


# ---------------------------------------------------------------------------
# Tool handlers (wrap real domain functions)
# ---------------------------------------------------------------------------

def _h_compute_nh3(args: Dict[str, Any], ctx: ToolContext) -> Dict[str, Any]:
    nh3, f = chemistry.unionized_ammonia_mgL(
        TAN_mgL=float(args["TAN_mgL"]), T_C=float(args["T_C"]), pH=float(args["pH"]))
    pKa = chemistry.ammonia_pka(float(args["T_C"]))
    return {"nh3_mgL": round(nh3, 6), "fraction": round(f, 6),
            "pKa": round(pKa, 4), "units": "mg/L NH3-N"}


def _h_do_saturation(args: Dict[str, Any], ctx: ToolContext) -> Dict[str, Any]:
    T_C = float(args["T_C"])
    sal = float(args.get("salinity_ppt") or 0.0)
    sat = chemistry.do_saturation_freshwater(T_C, sal)
    pct = None
    if "DO_mgL" in args and args["DO_mgL"] is not None:
        pct = chemistry.do_percent_saturation(float(args["DO_mgL"]), T_C, sal)
    return {"do_sat_mgL": round(sat, 4), "do_pct_sat": round(pct, 2) if pct is not None else None,
            "T_C": T_C, "salinity_ppt": sal}


def _h_tan_production(args: Dict[str, Any], ctx: ToolContext) -> Dict[str, Any]:
    g = biofilter.tan_production_from_feed(
        float(args["feed_kg_day"]),
        args.get("protein_pct") and float(args["protein_pct"]) or None)
    return {"tan_g_day": round(g, 3), "feed_kg_day": float(args["feed_kg_day"])}


def _h_biofilter_capacity(args: Dict[str, Any], ctx: ToolContext) -> Dict[str, Any]:
    media_key = args["biofilter_type"]
    if ctx.species_registry is not None:
        media = ctx.species_registry.media(media_key)
    else:
        media = {"specific_surface_area_m2_per_m3": 500,
                 "ref_tan_capacity_g_per_m2_day": 1.5}
    area = float(args["biofilter_area_m2"])
    ref_cap = float(media["ref_tan_capacity_g_per_m2_day"])
    T_C = float(args["T_C"])
    cap = biofilter.biofilter_capacity_derated(area, ref_cap, T_C)
    penalty = biofilter.nitrification_penalty_pct(T_C)
    return {"capacity_g_day": round(cap, 3),
            "nitrification_penalty_pct": penalty,
            "derating_factor": round(biofilter.nitrification_derating_factor(T_C), 4)}


def _h_match_diseases(args: Dict[str, Any], ctx: ToolContext) -> Dict[str, Any]:
    conds = args.get("conditions", [])
    warnings = diseases.match_disease_signals(conds)
    return {"signals": [w.to_dict() for w in warnings]}


def _h_query_knowledge(args: Dict[str, Any], ctx: ToolContext) -> Dict[str, Any]:
    keywords = [k.lower() for k in args.get("keywords", [])]
    text = ctx.knowledge_base_text or ""
    if not text:
        return {"citations": [], "coverage": "low", "note": "knowledge base empty"}
    # Simple relevance scoring: count keyword hits per paragraph (split by blank line).
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    scored = []
    for i, p in enumerate(paragraphs):
        pl = p.lower()
        hits = sum(pl.count(k) for k in keywords)
        if hits > 0:
            scored.append((hits, i, p.strip()))
    scored.sort(key=lambda x: (-x[0], x[1]))
    top = scored[:5]
    coverage = "high" if len(top) >= 3 else "medium" if top else "low"
    return {
        "citations": [p for _, _, p in top],
        "coverage": coverage,
        "matched_paragraphs": len(top),
    }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def _build_default_tools() -> List[Tool]:
    return [
        Tool(
            name="compute_nh3",
            description="Compute un-ionized ammonia NH3-N (mg/L) from TAN, temperature, and pH via Emerson (1975).",
            input_schema={"type": "object", "required": ["TAN_mgL", "T_C", "pH"],
                          "properties": {"TAN_mgL": {"type": "number"}, "T_C": {"type": "number"}, "pH": {"type": "number"}}},
            output_schema={"type": "object", "properties": {"nh3_mgL": {"type": "number"}, "fraction": {"type": "number"}, "pKa": {"type": "number"}}},
            handler=_h_compute_nh3, tags=["chemistry", "ammonia"],
        ),
        Tool(
            name="compute_do_saturation",
            description="Compute dissolved-oxygen saturation (mg/L and optional % saturation) vs temperature & salinity (Benson-Krause/APHA).",
            input_schema={"type": "object", "required": ["T_C"],
                          "properties": {"T_C": {"type": "number"}, "DO_mgL": {"type": "number"}, "salinity_ppt": {"type": "number"}}},
            output_schema={"type": "object", "properties": {"do_sat_mgL": {"type": "number"}, "do_pct_sat": {"type": "number"}}},
            handler=_h_do_saturation, tags=["chemistry", "oxygen"],
        ),
        Tool(
            name="compute_tan_production",
            description="Estimate daily TAN production (g/day) from feed load and protein %.",
            input_schema={"type": "object", "required": ["feed_kg_day"],
                          "properties": {"feed_kg_day": {"type": "number"}, "protein_pct": {"type": "number"}}},
            output_schema={"type": "object", "properties": {"tan_g_day": {"type": "number"}}},
            handler=_h_tan_production, tags=["biofilter"],
        ),
        Tool(
            name="compute_biofilter_capacity",
            description="Compute derated biofilter TAN removal capacity (g/day) for a media type and temperature.",
            input_schema={"type": "object", "required": ["biofilter_type", "biofilter_area_m2", "T_C"],
                          "properties": {"biofilter_type": {"type": "string"}, "biofilter_area_m2": {"type": "number"}, "T_C": {"type": "number"}}},
            output_schema={"type": "object", "properties": {"capacity_g_day": {"type": "number"}, "nitrification_penalty_pct": {"type": "number"}}},
            handler=_h_biofilter_capacity, tags=["biofilter"],
        ),
        Tool(
            name="match_disease_signals",
            description="Match observed stress/environmental condition tags against the cold-water disease early-warning rule table.",
            input_schema={"type": "object", "required": ["conditions"],
                          "properties": {"conditions": {"type": "array", "items": {"type": "string"}}}},
            output_schema={"type": "object", "properties": {"signals": {"type": "array"}}},
            handler=_h_match_diseases, tags=["disease"],
        ),
        Tool(
            name="query_knowledge_base",
            description="Keyword-search the cached SECOND-KNOWLEDGE-BRAIN.md text and return the most relevant paragraphs with a coverage rating.",
            input_schema={"type": "object", "required": ["keywords"],
                          "properties": {"keywords": {"type": "array", "items": {"type": "string"}}}},
            output_schema={"type": "object", "properties": {"citations": {"type": "array"}, "coverage": {"type": "string"}}},
            handler=_h_query_knowledge, tags=["knowledge", "rag"],
        ),
    ]


class ToolRegistry:
    """Resolves tools by name and executes them with validated arguments."""

    def __init__(self, tools: Optional[List[Tool]] = None) -> None:
        self._tools: Dict[str, Tool] = {t.name: t for t in (tools or _build_default_tools())}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise ToolError(f"unknown tool '{name}'. Available: {sorted(self._tools.keys())}")
        return self._tools[name]

    def list(self) -> List[str]:
        return sorted(self._tools.keys())

    def schemas(self) -> List[Dict[str, Any]]:
        return [{"name": t.name, "description": t.description,
                 "input_schema": t.input_schema, "output_schema": t.output_schema,
                 "tags": t.tags} for t in self._tools.values()]

    def invoke(self, name: str, args: Dict[str, Any], ctx: ToolContext) -> Any:
        tool = self.get(name)
        return tool.run(args, ctx)
