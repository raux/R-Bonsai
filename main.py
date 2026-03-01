from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Dict

app = FastAPI(title="R-Bonsai")

MAX_OUTPUT_LENGTH = 500_000


class LSystemRequest(BaseModel):
    iterations: int = Field(..., ge=1, le=10)
    axiom: str = Field(..., min_length=1, max_length=100)
    rules: Dict[str, str] = Field(default_factory=dict)


@app.post("/api/generate")
def generate(request: LSystemRequest):
    """Apply L-system rewriting rules for the given number of iterations."""
    current = request.axiom
    for _ in range(request.iterations):
        parts = [request.rules.get(char, char) for char in current]
        current = "".join(parts)
        if len(current) > MAX_OUTPUT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Generated string exceeds {MAX_OUTPUT_LENGTH:,} characters. "
                    "Reduce iterations."
                ),
            )
    return {"result": current}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
