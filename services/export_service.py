from __future__ import annotations

from datetime import datetime
from pathlib import Path

from models.runner_profile import RunnerProfile
from models.workout_result import WorkoutResult


def export_summary_txt(profile: RunnerProfile, result: WorkoutResult, output_dir: Path = Path("results")) -> Path:
    """Export final summary bundle into a text file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"coachme_summary_{timestamp}.txt"

    with path.open("w", encoding="utf-8") as f:
        f.write("CoachMe Workout Summary\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n")

        f.write("Athlete Profile\n")
        f.write(f"Name: {profile.name}\n")
        f.write(f"Event: {profile.event_specialization}\n")
        f.write(f"Weight (lbs): {profile.weight_lbs}\n")
        f.write(f"Biological sex: {profile.biological_sex}\n")
        f.write(f"Age: {profile.age}\n")
        f.write(f"Height (cm): {profile.height_cm}\n")
        f.write("PRs:\n")
        for event, pr in profile.personal_records.items():
            f.write(f"  - {event}: {pr}\n")
        f.write(f"No prior workout plan: {profile.no_prior_workout_plan}\n")
        f.write(f"Workout description: {profile.workout_description or 'N/A'}\n\n")

        f.write("AI-Style Summary\n")
        f.write(result.ai_summary + "\n\n")
        f.write("Future Workout Suggestion\n")
        f.write(result.future_workout_suggestion + "\n\n")
        f.write("Following Day Suggestion\n")
        f.write(result.next_day_suggestion + "\n\n")

        f.write("Split Review\n")
        f.write("Split #\tElapsed Time\tSplit Time\tStatus\n")
        for split in result.splits:
            f.write(f"{split.split_number}\t{split.elapsed_time}\t{split.split_time}\t{split.status}\n")

    return path
