from __future__ import annotations

import customtkinter as ctk

from models.runner_profile import RunnerProfile
from models.workout_result import SplitEntry, WorkoutResult
from services.export_service import export_summary_txt
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
        self.workout_result = self._build_mock_workout_result(primary_event)
        self.workout_page.set_splits(self.workout_result.splits)
        self.show_page(self.workout_page)

    def on_end_workout(self):
        self.show_page(self.final_loading_page)
        self.after(1500, self._show_final_summary)

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
    def _build_mock_workout_result(event: str) -> WorkoutResult:
        if event in {"100m", "200m"}:
            target = 5.0
            mock = [
                SplitEntry(1, "00:05.1", "00:05.1", "on_pace"),
                SplitEntry(2, "00:10.6", "00:05.5", "slow"),
                SplitEntry(3, "00:15.2", "00:04.6", "fast"),
                SplitEntry(4, "00:20.3", "00:05.1", "on_pace"),
            ]
        elif event in {"400m", "800m"}:
            target = 20.0
            mock = [
                SplitEntry(1, "00:20.2", "00:20.2", "on_pace"),
                SplitEntry(2, "00:41.0", "00:20.8", "slow"),
                SplitEntry(3, "01:00.0", "00:19.0", "fast"),
                SplitEntry(4, "01:20.2", "00:20.2", "on_pace"),
            ]
        else:
            target = 45.0
            mock = [
                SplitEntry(1, "00:45.2", "00:45.2", "on_pace"),
                SplitEntry(2, "01:33.1", "00:47.9", "slow"),
                SplitEntry(3, "02:17.0", "00:43.9", "fast"),
                SplitEntry(4, "03:01.8", "00:44.8", "on_pace"),
            ]
        return WorkoutResult(target_split_seconds=target, splits=mock)
