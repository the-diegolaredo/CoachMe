from __future__ import annotations

import customtkinter as ctk


class FinalSummaryPage(ctk.CTkFrame):
    def __init__(self, parent, on_download, on_return):
        super().__init__(parent)
        self.on_download = on_download
        self.on_return = on_return
        self._expanded = False

        ctk.CTkLabel(self, text="Workout Summary", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(16, 8))

        self.summary_label = ctk.CTkLabel(self, text="", justify="left", wraplength=900)
        self.summary_label.pack(fill="x", padx=20, pady=6)

        self.future_label = ctk.CTkLabel(self, text="", justify="left", wraplength=900)
        self.future_label.pack(fill="x", padx=20, pady=6)

        self.next_day_label = ctk.CTkLabel(self, text="", justify="left", wraplength=900)
        self.next_day_label.pack(fill="x", padx=20, pady=6)

        self.toggle_button = ctk.CTkButton(self, text="Show Split Review ▼", command=self._toggle_splits)
        self.toggle_button.pack(fill="x", padx=20, pady=(10, 6))

        self.splits_container = ctk.CTkFrame(self)
        self.splits_container.pack(fill="both", expand=False, padx=20, pady=(0, 8))
        self.splits_container.pack_forget()

        self.download_button = ctk.CTkButton(self, text="DOWNLOAD SUMMARY", height=44, command=self.on_download)
        self.download_button.pack(fill="x", padx=20, pady=6)

        self.return_button = ctk.CTkButton(self, text="RETURN TO BEGINNING", height=44, command=self.on_return)
        self.return_button.pack(fill="x", padx=20, pady=(0, 20))

    def set_content(self, summary: str, future: str, next_day: str, splits):
        self.summary_label.configure(text=f"AI-style summary:\n{summary}")
        self.future_label.configure(text=f"Future workout suggestion:\n{future}")
        self.next_day_label.configure(text=f"Following-day suggestion:\n{next_day}")
        self._render_splits(splits)

    def _render_splits(self, splits):
        for child in self.splits_container.winfo_children():
            child.destroy()

        header = ctk.CTkLabel(self.splits_container, text="Split #    Elapsed Time    Split Time    Status", font=ctk.CTkFont(weight="bold"))
        header.pack(anchor="w", padx=8, pady=(8, 2))

        for s in splits:
            row_text = f"{s.split_number:<9} {s.elapsed_time:<14} {s.split_time:<11} {s.status}"
            ctk.CTkLabel(self.splits_container, text=row_text, anchor="w", justify="left").pack(anchor="w", padx=8, pady=1)

    def _toggle_splits(self):
        self._expanded = not self._expanded
        if self._expanded:
            self.splits_container.pack(fill="both", expand=False, padx=20, pady=(0, 8))
            self.toggle_button.configure(text="Hide Split Review ▲")
        else:
            self.splits_container.pack_forget()
            self.toggle_button.configure(text="Show Split Review ▼")
