from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class ModeDefinition:
    name: str
    axiom: str
    rules: Dict[str, str]
    angle: float


MODES: Dict[int, ModeDefinition] = {
    0: ModeDefinition(
        name="Classic Bonsai",
        axiom="X",
        rules={"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"},
        angle=25.0,
    ),
    1: ModeDefinition(
        name="Koch Snowflake",
        axiom="F++F++F",
        rules={"F": "F-F++F-F"},
        angle=60.0,
    ),
}


def get_mode(mode_id: int) -> Optional[ModeDefinition]:
    return MODES.get(mode_id)


def generate_lsystem(axiom: str, rules: Dict[str, str], iterations: int) -> str:
    if iterations < 0:
        raise ValueError("iterations must be non-negative")

    current = axiom
    for _ in range(iterations):
        next_sequence = []
        for symbol in current:
            replacement = rules.get(symbol, symbol)
            next_sequence.append(replacement)
        current = "".join(next_sequence)
    return current
