from __future__ import annotations

import customtkinter as ctk

from coachme import SplitEvent
from models.runner_profile import RunnerProfile
from models.workout_result import SplitEntry, WorkoutResult
from services.export_service import export_summary_txt
from services.split_tracking_service import SplitTrackingService, TrackingConfig
from services.summary_generator import (
    future_workout_suggestion,
    generate_rule_based_summary,
    next_day_suggestion,
)
from ui.pages.final_summary_page import FinalSummaryPage
from ui.pages.input_page import InputPage
from ui.pages.loading_page import LoadingPage
from ui.pages.pre_workout_page import PreWorkoutPage
from ui.pages.workout_page import WorkoutPage


class CoachMeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CoachMe - Track Coach Prototype")
        self.geometry("1024x760")

        self.profile = RunnerProfile()
        self.workout_result = WorkoutResult(target_split_seconds=20.0)
        self.split_tracker = SplitTrackingService()

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=8, pady=8)

        self.input_page = InputPage(self.container, on_continue=self.on_input_continue)
        self.loading_page = LoadingPage(self.container, message="Processing athlete profile...")
        self.pre_workout_page = PreWorkoutPage(self.container, on_start=self.on_start_workout)
        self.workout_page = WorkoutPage(self.container, on_end=self.on_end_workout)
        self.final_loading_page = LoadingPage(self.container, message="Analyzing workout...")
        self.final_summary_page = FinalSummaryPage(
            self.container,
            on_download=self.on_download_summary,
            on_return=self.on_return_to_beginning,
        )

        self.current_page = None
        self.show_page(self.input_page)

    def show_page(self, page):
        if self.current_page is not None:
            self.current_page.pack_forget()
        self.current_page = page
        self.current_page.pack(fill="both", expand=True)

    def on_input_continue(self, payload: dict):
        self.profile = RunnerProfile(
            name=payload["name"],
            event_specialization=payload["event_specialization"],
            weight_lbs=self._to_float(payload["weight_lbs"]),
            biological_sex=payload["biological_sex"],
            age=self._to_int(payload["age"]),
            height_cm=self._to_float(payload["height_cm"]),
            personal_records=payload["personal_records"],
            workout_description=payload["workout_description"],
            no_prior_workout_plan=payload["no_prior_workout_plan"],
        )

        self.show_page(self.loading_page)
        self.after(1500, self._show_pre_workout_summary)

    def _show_pre_workout_summary(self):
        workout_text = self.profile.workout_description if self.profile.workout_description else "No prior workout plan provided."
        events_text = ", ".join(self.profile.event_specialization)
        summary = (
            f"Hi {self.profile.name}!\n\n"
            f"Goal event(s): {events_text}\n"
            f"Profile: {self.profile.age} years old, {self.profile.biological_sex}, "
            f"{self.profile.height_cm} cm, {self.profile.weight_lbs} lbs\n"
            f"Current PRs: {self.profile.personal_records or 'No PRs entered'}\n"
            f"Workout description: {workout_text}"
        )
        self.pre_workout_page.set_summary(summary)
        self.show_page(self.pre_workout_page)

    def on_start_workout(self):
        primary_event = self.profile.event_specialization[0]
        self.workout_result = WorkoutResult(target_split_seconds=self._target_for_event(primary_event), splits=[])
        self.workout_page.clear_splits()
        self.show_page(self.workout_page)

        config = TrackingConfig(headless=True, mute=True)
        self.split_tracker.start(config=config, on_split_detected=self._on_split_detected)

    def _on_split_detected(self, split_event: SplitEvent):
        elapsed = self._format_seconds(split_event.elapsed_seconds)
        split_time = self._format_seconds(split_event.split_seconds)
        status = self._status_from_target(split_event.split_seconds, self.workout_result.target_split_seconds)
        split_entry = SplitEntry(split_event.crossing_number, elapsed, split_time, status)
        self.workout_result.splits.append(split_entry)

        self.after(0, lambda: self.workout_page.add_split_row(split_entry.split_number, split_entry.elapsed_time, split_entry.split_time, split_entry.status))

    def on_end_workout(self):
        self.split_tracker.stop()
        self.show_page(self.final_loading_page)
        self.after(1200, self._show_final_summary)

    def _show_final_summary(self):
        self.workout_result.ai_summary = generate_rule_based_summary(self.profile, self.workout_result)
        primary_event = self.profile.event_specialization[0]
        self.workout_result.future_workout_suggestion = future_workout_suggestion(primary_event)
        self.workout_result.next_day_suggestion = next_day_suggestion(primary_event)

        self.final_summary_page.set_content(
            summary=self.workout_result.ai_summary,
            future=self.workout_result.future_workout_suggestion,
            next_day=self.workout_result.next_day_suggestion,
            splits=self.workout_result.splits,
        )
        self.show_page(self.final_summary_page)

    def on_download_summary(self):
        path = export_summary_txt(self.profile, self.workout_result)
        self.final_summary_page.download_button.configure(text=f"Downloaded: {path.name}")

    def on_return_to_beginning(self):
        self.final_summary_page.download_button.configure(text="DOWNLOAD SUMMARY")
        self.input_page.reset_fields()
        self.show_page(self.input_page)

    @staticmethod
    def _to_float(value: str):
        try:
            return float(value) if value else None
        except ValueError:
            return None

    @staticmethod
    def _to_int(value: str):
        try:
            return int(value) if value else None
        except ValueError:
            return None

    @staticmethod
    def _target_for_event(event: str) -> float:
        if event in {"100m", "200m"}:
            return 5.0
        if event in {"400m", "800m"}:
            return 20.0
        return 45.0

    @staticmethod
    def _status_from_target(split_seconds: float, target: float) -> str:
        if split_seconds > target * 1.06:
            return "slow"
        if split_seconds < target * 0.94:
            return "fast"
        return "on_pace"

    @staticmethod
    def _format_seconds(total_seconds: float) -> str:
        minutes = int(total_seconds // 60)
        seconds = total_seconds - (minutes * 60)
        return f"{minutes:02d}:{seconds:04.1f}"
