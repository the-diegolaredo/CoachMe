from __future__ import annotations

import customtkinter as ctk


class LoadingPage(ctk.CTkFrame):
    def __init__(self, parent, message: str):
        super().__init__(parent)
        ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=24, weight="bold")).pack(expand=True)
