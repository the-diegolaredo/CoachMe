from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RunnerProfile:
    """Stores athlete inputs collected from the first page."""

    name: str = "Athlete"
    event_specialization: list[str] = field(default_factory=lambda: ["100m"])
    weight_lbs: float | None = None
    biological_sex: str = ""
    age: int | None = None
    height_cm: float | None = None
    personal_records: dict[str, str] = field(default_factory=dict)
    workout_description: str = ""
    no_prior_workout_plan: bool = False
