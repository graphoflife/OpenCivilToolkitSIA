"""
main.py – FastAPI application entry point.

Replaces the old server.py (SimpleHTTPRequestHandler) with a proper
FastAPI app that serves static files and exposes a REST API for all
computation. The JS frontend is a thin client that calls these endpoints.

Run with:
    uvicorn main:app --reload --port 8080
"""

import json
import os
from pathlib import Path
from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from civil_toolkit.engine.types import Plate, Material, Layer, MaterialType
from civil_toolkit.engine.material_engine import (
    BETON_VORLAGEN, STAHL_VORLAGEN,
    get_variable_defs, get_report_extras, get_all_property_keys,
    get_material_vars, create_default_properties,
)
from civil_toolkit.engine.plate_engine import (
    calculate_plate, create_new_plate, create_new_layer,
)

# ---------------------------------------------------------------------------
# Paths & persistence
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PROJECT_FILE = DATA_DIR / "project.json"

DEFAULT_PROJECT: Dict[str, Any] = {
    "settings": {"code": "SIA"},
    "activeApp": "materials",
    "materials": [],
    "plates": [],
}


def _load_project() -> Dict[str, Any]:
    if PROJECT_FILE.exists():
        try:
            return json.loads(PROJECT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULT_PROJECT.copy()


def _save_project(data: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    PROJECT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="OpenCivilToolkit API", version="2.0.0")


# ---------------------------------------------------------------------------
# Project endpoints  (replaces persistence.js logic)
# ---------------------------------------------------------------------------

@app.get("/api/project")
def get_project() -> JSONResponse:
    return JSONResponse(_load_project())


@app.post("/api/project")
async def save_project(request_body: Dict[str, Any]) -> JSONResponse:
    try:
        _save_project(request_body)
        return JSONResponse({"status": "success"})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Material endpoints
# ---------------------------------------------------------------------------

@app.get("/api/materials/templates")
def get_material_templates() -> JSONResponse:
    concrete_templates = {k.value: v.model_dump() for k, v in BETON_VORLAGEN.items()}
    steel_templates = {k.value: v.model_dump() for k, v in STAHL_VORLAGEN.items()}
    return JSONResponse({
        "concrete": concrete_templates,
        "steel": steel_templates,
    })


class MaterialCalcRequest(BaseModel):
    material: Material


@app.post("/api/materials/calculate")
def calculate_material(req: MaterialCalcRequest) -> JSONResponse:
    """
    Calculates all MyVar values for a material and returns
    pre-rendered LaTeX equations for the report.
    """
    mat = req.material
    try:
        vars_ = get_material_vars(mat)
        defs = get_variable_defs(mat.type)
        extras = get_report_extras(mat.type)

        equations = []
        for d in defs:
            v = vars_.get(d.id)
            if not v:
                continue
            v_dict = v.to_dict()
            equations.append({
                "description": d.description,
                "reference": v.reference,
                "overridden": v.overridden,
                "active": v.active,
                "editor": {k: v for k, v in asdict(d.editor).items() if v is not None},
                **v_dict,
                "var_id": d.id,
                "id": d.id,  # Keep clean symbol ID (e.g. 'f_cd') for diagram lookup & tracing
                "prop": str(d.id),  # storage key now equals the VarId string
            })

        return JSONResponse({
            "equations": equations,
            "extras": [asdict(e) for e in extras],
            "all_property_keys": get_all_property_keys(mat.type),
        })
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


class DefaultPropertiesRequest(BaseModel):
    type: MaterialType
    grade: str


@app.post("/api/materials/default-properties")
def get_default_properties(req: DefaultPropertiesRequest) -> JSONResponse:
    return JSONResponse(create_default_properties(req.type, req.grade))


# ---------------------------------------------------------------------------
# Plate endpoints
# ---------------------------------------------------------------------------

class PlateCalcRequest(BaseModel):
    plate: Plate
    materials: List[Material]


@app.post("/api/plates/calculate")
def calc_plate(req: PlateCalcRequest) -> JSONResponse:
    """
    Runs the full plate calculation and returns sections with pre-rendered LaTeX.
    The JS frontend only needs to pass `section.latex` to KaTeX.
    """
    try:
        result = calculate_plate(req.plate, req.materials)
        # vars_ contains MyVar objects — serialise to dicts
        vars_serialised = {
            k: v.to_dict() if hasattr(v, "to_dict") else v
            for k, v in result["vars"].items()
            if not k.startswith("_")  # skip internal accumulators
        }
        # Serialise computed layers: Location enum keys → 'bottom'/'top' for JS compat
        from civil_toolkit.engine.types import Location
        _loc_key = {Location.BOT: "bottom", Location.TOP: "top"}
        _default = lambda o: o.model_dump() if hasattr(o, "model_dump") else o.__dict__
        computed_serialised = {
            _loc_key[loc]: json.loads(json.dumps(layers, default=_default))
            for loc, layers in result["computed"].items()
        }
        return JSONResponse({
            "vars": vars_serialised,
            "sections": result["sections"],
            "computed": computed_serialised,
        })
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


class NewPlateRequest(BaseModel):
    name: str
    materials: List[Material] = []


@app.post("/api/plates/new")
def new_plate(req: NewPlateRequest) -> JSONResponse:
    return JSONResponse(create_new_plate(req.name, req.materials).model_dump())


@app.post("/api/plates/new-layer")
def new_layer(main_dir: str = "x") -> JSONResponse:
    return JSONResponse(create_new_layer(main_dir).model_dump())


# ---------------------------------------------------------------------------
# Serve static files (index.html, style.css, js/)
# Must be LAST so API routes take priority.
# ---------------------------------------------------------------------------

app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
