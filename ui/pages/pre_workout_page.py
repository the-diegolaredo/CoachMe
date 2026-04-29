from __future__ import annotations

import customtkinter as ctk


class PreWorkoutPage(ctk.CTkFrame):
    def __init__(self, parent, on_start):
        super().__init__(parent)
        self.on_start = on_start

        self.title_label = ctk.CTkLabel(self, text="Welcome!", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        self.summary_label = ctk.CTkLabel(self, text="", justify="left", wraplength=900)
        self.summary_label.pack(fill="x", padx=20)

        self.start_btn = ctk.CTkButton(self, text="START", height=50, font=ctk.CTkFont(size=20, weight="bold"), command=self.on_start)
        self.start_btn.pack(side="bottom", fill="x", padx=20, pady=20)

    def set_summary(self, text: str):
        self.summary_label.configure(text=text)
