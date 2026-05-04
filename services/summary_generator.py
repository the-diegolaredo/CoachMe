from __future__ import annotations

from models.runner_profile import RunnerProfile
from models.workout_result import WorkoutResult


def generate_rule_based_summary(profile: RunnerProfile, result: WorkoutResult) -> str:
    """Simple placeholder summary generator (no LLM yet)."""
    split_count = len(result.splits)
    if split_count == 0:
        return "Nice work showing up today. Next time, let's capture more split checkpoints."

    slower = sum(1 for s in result.splits if s.status == "slow")
    faster = sum(1 for s in result.splits if s.status == "fast")
    on_pace = sum(1 for s in result.splits if s.status == "on_pace")
    events_text = ", ".join(profile.event_specialization)

    return (
        f"Great effort in your {events_text} focus session. "
        f"You logged {split_count} splits: {on_pace} on pace, {slower} slower than target, "
        f"and {faster} faster than target. "
        "Primary coaching note: keep your middle splits controlled, then finish strong with relaxed form."
    )


def future_workout_suggestion(event: str) -> str:
    """One simple future workout suggestion matched to event."""
    if event in {"100m", "200m"}:
        return "Future workout: 6 x 80m fast strides at 90-95% effort, full walk-back recovery."
    if event in {"400m", "800m"}:
        return "Future workout: 5 x 300m at goal pace with 2:00 rest to build race rhythm."
    return "Future workout: 4 x 800m at controlled threshold pace with 2:30 jog recovery."


def next_day_suggestion(event: str) -> str:
    """One following-day suggestion for recovery/cross-training."""
    if event in {"100m", "200m"}:
        return "Following day: 20-30 min easy bike + light mobility + glute activation."
    return "Following day: 25-40 min easy recovery run + core stability circuit + stretching."
