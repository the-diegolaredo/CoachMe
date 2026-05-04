from __future__ import annotations

import customtkinter as ctk


STATUS_DISPLAY = {
    "slow": ("▲", "#d92d20", "Slower than target"),
    "fast": ("▼", "#f5b700", "Too much faster than target"),
    "on_pace": ("✓", "#1a7f37", "On pace"),
}


class WorkoutPage(ctk.CTkFrame):
    def __init__(self, parent, on_end):
        super().__init__(parent)
        self.on_end = on_end

        ctk.CTkLabel(self, text="Workout In Progress", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(16, 8))

        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=8)

        self._render_header()

        end_button = ctk.CTkButton(
            self,
            text="END WORKOUT",
            height=48,
            fg_color="#b42318",
            hover_color="#912018",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.on_end,
        )
        end_button.pack(fill="x", padx=20, pady=(8, 20))

    def _render_header(self):
        headers = ["Split #", "Elapsed Time", "Split Time", "Status"]
        row = ctk.CTkFrame(self.table_frame)
        row.pack(fill="x", padx=8, pady=6)
        for text in headers:
            ctk.CTkLabel(row, text=text, font=ctk.CTkFont(weight="bold"), width=200).pack(side="left", padx=4)

    def clear_splits(self):
        for child in self.table_frame.winfo_children()[1:]:
            child.destroy()

    def add_split_row(self, split_number: int, elapsed_time: str, split_time: str, status: str):
        icon, color, label = STATUS_DISPLAY.get(status, ("?", "gray", "Unknown"))
        row = ctk.CTkFrame(self.table_frame)
        row.pack(fill="x", padx=8, pady=3)
        ctk.CTkLabel(row, text=str(split_number), width=200).pack(side="left", padx=4)
        ctk.CTkLabel(row, text=elapsed_time, width=200).pack(side="left", padx=4)
        ctk.CTkLabel(row, text=split_time, width=200).pack(side="left", padx=4)

        status_frame = ctk.CTkFrame(row, fg_color="transparent")
        status_frame.pack(side="left", padx=4)
        ctk.CTkLabel(status_frame, text=icon, text_color=color, font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        ctk.CTkLabel(status_frame, text=label).pack(side="left", padx=6)
