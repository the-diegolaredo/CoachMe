from __future__ import annotations

import customtkinter as ctk


class InputPage(ctk.CTkFrame):
    def __init__(self, parent, on_continue):
        super().__init__(parent)
        self.on_continue = on_continue

        self.event_options = ["100m", "200m", "400m", "800m", "1600m", "3200m"]

        title = ctk.CTkLabel(self, text="Athlete Input", font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=(16, 8))

        self.name_entry = self._entry_row("Name", "Athlete")
        self.event_menu = self._menu_row("Event specialization", self.event_options)
        self.weight_entry = self._entry_row("Weight (lbs)", "150")
        self.sex_menu = self._menu_row("Biological sex", ["Female", "Male", "Intersex", "Prefer not to say"])
        self.age_entry = self._entry_row("Age", "16")
        self.height_entry = self._entry_row("Height (cm)", "170")

        pr_frame = ctk.CTkFrame(self)
        pr_frame.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(pr_frame, text="Current PRs (time)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(8, 4))
        self.pr_entries = {}
        for event in self.event_options:
            row = ctk.CTkFrame(pr_frame)
            row.pack(fill="x", padx=8, pady=2)
            ctk.CTkLabel(row, text=event, width=80, anchor="w").pack(side="left", padx=(4, 8))
            entry = ctk.CTkEntry(row, placeholder_text="e.g. 12.45 or 2:15")
            entry.pack(side="left", fill="x", expand=True, padx=(0, 4), pady=2)
            self.pr_entries[event] = entry

        self.no_plan_var = ctk.BooleanVar(value=False)
        self.no_plan_checkbox = ctk.CTkCheckBox(
            self,
            text="No prior workout plan",
            variable=self.no_plan_var,
            command=self._toggle_workout_box,
        )
        self.no_plan_checkbox.pack(anchor="w", padx=24, pady=(8, 2))

        ctk.CTkLabel(self, text="Workout description").pack(anchor="w", padx=24)
        self.workout_text = ctk.CTkTextbox(self, height=110)
        self.workout_text.pack(fill="x", padx=20, pady=(4, 10))

        self.continue_button = ctk.CTkButton(self, text="Continue", height=40, command=self._collect_and_continue)
        self.continue_button.pack(pady=(0, 16), padx=20, fill="x")

    def _entry_row(self, label, placeholder):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(frame, text=label, width=160, anchor="w").pack(side="left", padx=10)
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder)
        entry.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        return entry

    def _menu_row(self, label, values):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(frame, text=label, width=160, anchor="w").pack(side="left", padx=10)
        menu = ctk.CTkOptionMenu(frame, values=values)
        menu.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        return menu

    def _toggle_workout_box(self):
        if self.no_plan_var.get():
            self.workout_text.delete("1.0", "end")
            self.workout_text.configure(state="disabled")
        else:
            self.workout_text.configure(state="normal")

    def _collect_and_continue(self):
        workout_text = ""
        if not self.no_plan_var.get():
            workout_text = self.workout_text.get("1.0", "end").strip()

        payload = {
            "name": self.name_entry.get().strip() or "Athlete",
            "event_specialization": self.event_menu.get(),
            "weight_lbs": self.weight_entry.get().strip(),
            "biological_sex": self.sex_menu.get(),
            "age": self.age_entry.get().strip(),
            "height_cm": self.height_entry.get().strip(),
            "personal_records": {event: entry.get().strip() for event, entry in self.pr_entries.items() if entry.get().strip()},
            "workout_description": workout_text,
            "no_prior_workout_plan": self.no_plan_var.get(),
        }
        self.on_continue(payload)
