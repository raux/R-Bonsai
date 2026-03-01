from dataclasses import asdict
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from .lsystem import MODES, ModeDefinition, generate_lsystem, get_mode

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DEFAULT_ANGLE = 25.0

app = FastAPI(title="R-Bonsai L-System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class GenerateRequest(BaseModel):
    iterations: int = Field(..., ge=0, le=10)
    axiom: str = Field(..., min_length=1)
    rules: Dict[str, str]
    angle: Optional[float] = None
    mode: Optional[int] = Field(None, description="Optional preset mode")

    @field_validator("rules")
    def validate_rules(cls, value: Dict[str, str]) -> Dict[str, str]:
        if not value:
            raise ValueError("rules must not be empty")
        return value


class GenerateResponse(BaseModel):
    result: str
    iterations: int
    axiom: str
    rules: Dict[str, str]
    angle: float
    mode: Optional[int] = None


class ModeResponse(BaseModel):
    name: str
    axiom: str
    rules: Dict[str, str]
    angle: float


def resolve_payload(payload: GenerateRequest) -> tuple[str, Dict[str, str], float, Optional[ModeDefinition]]:
    mode_definition = get_mode(payload.mode) if payload.mode is not None else None
    if payload.mode is not None and mode_definition is None:
        raise HTTPException(status_code=400, detail="Unknown mode")

    axiom = mode_definition.axiom if mode_definition else payload.axiom
    rules = mode_definition.rules if mode_definition else payload.rules

    resolved_angle = payload.angle
    if resolved_angle is None:
        resolved_angle = mode_definition.angle if mode_definition else DEFAULT_ANGLE

    return axiom, rules, resolved_angle, mode_definition


@app.get("/", response_class=FileResponse)
async def serve_index() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Index file not found")
    return FileResponse(index_path)


@app.get("/api/modes", response_model=Dict[int, ModeResponse])
async def list_modes() -> Dict[int, ModeResponse]:
    return {mode_id: ModeResponse(**asdict(mode)) for mode_id, mode in MODES.items()}


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest) -> GenerateResponse:
    axiom, rules, angle, mode_definition = resolve_payload(payload)
    result = generate_lsystem(axiom, rules, payload.iterations)

    return GenerateResponse(
        result=result,
        iterations=payload.iterations,
        axiom=axiom,
        rules=rules,
        angle=angle,
        mode=payload.mode,
    )
