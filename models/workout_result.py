from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SplitEntry:
    split_number: int
    elapsed_time: str
    split_time: str
    status: str


@dataclass
class WorkoutResult:
    """Stores mock split table and summary text outputs."""

    target_split_seconds: float
    splits: list[SplitEntry] = field(default_factory=list)
    ai_summary: str = ""
    future_workout_suggestion: str = ""
    next_day_suggestion: str = ""
