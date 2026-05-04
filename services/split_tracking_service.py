from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from coachme import SplitEvent, run_split_tracking


@dataclass
class TrackingConfig:
    source: int = 0
    width: int = 640
    height: int = 480
    line_x: int = -1
    direction: str = "left_to_right"
    min_area: int = 2500
    cooldown: float = 1.5
    output: Path = Path("results/splits.csv")
    summary_txt: Path = Path("results/latest_workout.txt")
    headless: bool = True
    mute: bool = True
    use_picamera2: bool = False


class SplitTrackingService:
    """Runs coachme split tracking in a background thread for GUI usage."""

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self.latest_splits: list[SplitEvent] = []
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self, config: TrackingConfig, on_split_detected: Callable[[SplitEvent], None]) -> None:
        if self._running:
            return

        self._stop_event = threading.Event()
        self.latest_splits = []

        def worker():
            self._running = True
            self.latest_splits = run_split_tracking(
                source=config.source,
                width=config.width,
                height=config.height,
                line_x=config.line_x,
                direction=config.direction,
                min_area=config.min_area,
                cooldown=config.cooldown,
                output=config.output,
                summary_txt=config.summary_txt,
                headless=config.headless,
                mute=config.mute,
                use_picamera2=config.use_picamera2,
                stop_event=self._stop_event,
                on_split_detected=on_split_detected,
                allow_terminal_stop=False,
            )
            self._running = False

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def stop(self) -> list[SplitEvent]:
        if self._running:
            self._stop_event.set()
            if self._thread is not None:
                self._thread.join(timeout=4)
        return self.latest_splits
