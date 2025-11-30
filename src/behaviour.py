from dataclasses import dataclass, field
from typing import List, Dict, Any, Union
import yaml
from pathlib import Path


# ---- Command Base Types ------------------------------------------------------

@dataclass
class Command:
    """Base class for all behaviour script commands."""
    pass


@dataclass
class Pause(Command):
    ticks: int = 0


@dataclass
class Pause4s(Command):
    """Represents a fixed 4-second pause."""
    pass


@dataclass
class TurnCW(Command):
    pass


@dataclass
class TurnCCW(Command):
    pass


@dataclass
class MoveRelative(Command):
    distance: float = 0.0


# A registry mapping YAML keys to Command classes
COMMAND_REGISTRY: Dict[str, Any] = {
    "Pause4s":         Pause4s,
    "TurnCW":          TurnCW,
    "TurnCCW":         TurnCCW,
    "MoveRelative":    MoveRelative,
    "Pause":           Pause,
}


# ---- Behaviour Class ---------------------------------------------------------

@dataclass
class Behaviour:
    index: int
    name: str
    script: List[Command] = field(default_factory=list)

    @staticmethod
    def load(index: int, base_path: str = "data/scripts") -> "Behaviour":
        """Load a behaviour YAML file by index."""
        path = Path(base_path) / f"behaviour{index}.yaml"
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        name = data.get("Name", f"Behaviour{index}")
        script_yaml = data.get("Script", [])

        script_commands: List[Command] = []
        for entry in script_yaml:
            if isinstance(entry, str):
                # simple command like "TurnCW"
                cls = COMMAND_REGISTRY.get(entry)
                if cls:
                    script_commands.append(cls())
            elif isinstance(entry, dict):
                # command with parameters
                key = next(iter(entry.keys()))
                params = entry[key] or {}
                cls = COMMAND_REGISTRY.get(key)
                if cls:
                    script_commands.append(cls(**params))

        return Behaviour(index=index, name=name, script=script_commands)
