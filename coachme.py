#!/usr/bin/env python3
"""CoachMe MVP: video capture, line crossing split timing, TTS announcements, and CSV logging."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2


@dataclass
class DetectionState:
    previous_center_x: Optional[int] = None
    last_crossing_ts: float = 0.0


class SplitAnnouncer:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def say(self, message: str) -> None:
        print(f"[announce] {message}")
        if not self.enabled:
            return

        commands = [
            ["espeak-ng", message],
            ["espeak", message],
            ["spd-say", message],
        ]
        for command in commands:
            try:
                subprocess.Popen(command)
                return
            except FileNotFoundError:
                continue


class VideoSource:
    def __init__(self, source: int, width: int, height: int, use_picamera2: bool = False) -> None:
        self.use_picamera2 = use_picamera2
        self.cap = None
        self.picam2 = None

        if use_picamera2:
            try:
                from picamera2 import Picamera2  # type: ignore
            except Exception as exc:  # pragma: no cover - optional runtime dependency
                raise RuntimeError(
                    "picamera2 backend requested, but picamera2 is unavailable. "
                    "Install with: sudo apt install python3-picamera2"
                ) from exc

            self.picam2 = Picamera2()
            config = self.picam2.create_video_configuration(main={"size": (width, height), "format": "RGB888"})
            self.picam2.configure(config)
            self.picam2.start()
        else:
            self.cap = cv2.VideoCapture(source)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            if not self.cap.isOpened():
                raise RuntimeError(f"Unable to open camera source {source}.")

    def read(self):
        if self.use_picamera2 and self.picam2 is not None:
            frame = self.picam2.capture_array()
            return True, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if self.cap is None:
            return False, None
        return self.cap.read()

    def release(self) -> None:
        if self.cap is not None:
            self.cap.release()
        if self.picam2 is not None:
            self.picam2.stop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CoachMe MVP split-timer")
    parser.add_argument("--source", type=int, default=0, help="Camera index for OpenCV backend (default: 0)")
    parser.add_argument("--width", type=int, default=640, help="Capture width")
    parser.add_argument("--height", type=int, default=480, help="Capture height")
    parser.add_argument("--line-x", type=int, default=-1, help="Virtual finish line X pixel (default: center)")
    parser.add_argument(
        "--direction",
        choices=["left_to_right", "right_to_left"],
        default="left_to_right",
        help="Required crossing direction",
    )
    parser.add_argument("--min-area", type=int, default=2500, help="Minimum contour area to treat as runner")
    parser.add_argument("--cooldown", type=float, default=1.5, help="Seconds between registered crossings")
    parser.add_argument("--output", type=Path, default=Path("results/splits.csv"), help="CSV output path")
    parser.add_argument("--headless", action="store_true", help="Disable preview window")
    parser.add_argument("--mute", action="store_true", help="Disable spoken split announcements")
    parser.add_argument("--use-picamera2", action="store_true", help="Use Raspberry Pi picamera2 backend")
    return parser.parse_args()


def ensure_output_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["crossing_number", "timestamp_utc_epoch", "elapsed_seconds", "split_seconds"])


def append_split(path: Path, crossing_number: int, elapsed: float, split: float) -> None:
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([crossing_number, time.time(), f"{elapsed:.2f}", f"{split:.2f}"])


def should_count_crossing(prev_x: int, current_x: int, line_x: int, direction: str) -> bool:
    if direction == "left_to_right":
        return prev_x < line_x <= current_x
    return prev_x > line_x >= current_x


def main() -> int:
    args = parse_args()
    announcer = SplitAnnouncer(enabled=not args.mute)

    try:
        source = VideoSource(
            source=args.source,
            width=args.width,
            height=args.height,
            use_picamera2=args.use_picamera2,
        )
    except RuntimeError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    background = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=50, detectShadows=False)

    state = DetectionState()
    run_started_at = time.time()
    last_split_elapsed = 0.0
    crossings = 0

    ensure_output_csv(args.output)
    announcer.say("CoachMe ready")

    try:
        while True:
            ok, frame = source.read()
            if not ok or frame is None:
                print("[warn] Frame capture failed; exiting.")
                break

            frame_h, frame_w = frame.shape[:2]
            line_x = args.line_x if args.line_x >= 0 else frame_w // 2

            fg_mask = background.apply(frame)
            fg_mask = cv2.GaussianBlur(fg_mask, (9, 9), 0)
            _, fg_mask = cv2.threshold(fg_mask, 180, 255, cv2.THRESH_BINARY)

            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            candidates = [c for c in contours if cv2.contourArea(c) >= args.min_area]

            if candidates:
                largest = max(candidates, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest)
                center_x = x + w // 2

                if state.previous_center_x is not None:
                    crossed = should_count_crossing(state.previous_center_x, center_x, line_x, args.direction)
                    cooldown_done = (time.time() - state.last_crossing_ts) >= args.cooldown
                    if crossed and cooldown_done:
                        now = time.time()
                        elapsed = now - run_started_at
                        split = elapsed - last_split_elapsed
                        crossings += 1
                        last_split_elapsed = elapsed
                        state.last_crossing_ts = now

                        append_split(args.output, crossings, elapsed, split)
                        announcer.say(f"Split {crossings}: {split:.1f} seconds")
                        print(f"[event] crossing={crossings} split={split:.2f}s elapsed={elapsed:.2f}s")

                state.previous_center_x = center_x

                if not args.headless:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(frame, (center_x, y + h // 2), 5, (255, 0, 0), -1)

            if not args.headless:
                cv2.line(frame, (line_x, 0), (line_x, frame_h), (0, 0, 255), 2)
                cv2.putText(
                    frame,
                    f"Crossings: {crossings}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2,
                )
                cv2.imshow("CoachMe", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
            else:
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[info] Interrupted by user.")
    finally:
        source.release()
        cv2.destroyAllWindows()

    print(f"[info] Session ended. Splits saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
