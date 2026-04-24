# CoachMe MVP (Raspberry Pi Track Split Timer)

Minimal, reliable prototype for a 1-month build timeline. This project:

1. captures video from a USB webcam (`/dev/video0`) or Raspberry Pi camera,
2. detects a runner crossing a virtual line,
3. announces split times with text-to-speech,
4. saves split results to CSV,
5. stays lightweight (OpenCV + standard library).

## Hardware used

- Raspberry Pi 4
- Camera (Logitech USB webcam or Pi camera module)
- Speaker HAT / powered speakers

## How it works (simple + robust)

- Uses OpenCV background subtraction to detect moving foreground blobs.
- Tracks the largest moving object's center point.
- Counts a split when center crosses a configurable vertical line (`line-x`) in your chosen direction.
- Uses a cooldown window to reduce duplicate triggers.
- Writes each split to `results/splits.csv` and announces over speakers.

> This is intentionally basic and dependable for MVP use, not full athlete ID or multi-runner tracking.

## Install

### 1) System packages (Raspberry Pi OS)

```bash
sudo apt update
sudo apt install -y python3-pip python3-opencv espeak-ng
```

If using Pi Camera with `picamera2` backend:

```bash
sudo apt install -y python3-picamera2
```

### 2) Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

### USB webcam (default)

```bash
python3 coachme.py --source 0
```

### Pi camera (`picamera2`)

```bash
python3 coachme.py --use-picamera2
```

Press `q` in the preview window to stop, or type `end` in the terminal and press Enter.

## Useful options

```bash
python3 coachme.py \
  --line-x 360 \
  --direction left_to_right \
  --min-area 2500 \
  --cooldown 1.5 \
  --output results/workout_1.csv
```

- `--line-x`: X pixel position for the virtual timing line (default = image center)
- `--direction`: `left_to_right` or `right_to_left`
- `--min-area`: ignores tiny moving objects/noise
- `--cooldown`: minimum seconds between valid crossings
- `--headless`: run without preview window (good for SSH)
- `--mute`: disable spoken announcements
- `--summary-txt`: text summary file rewritten at the end of each new workout (default: `results/latest_workout.txt`)

## Output files

`results/splits.csv` columns:

- `crossing_number`
- `timestamp_utc_epoch`
- `elapsed_seconds`
- `split_seconds`

`results/latest_workout.txt` is rewritten every run and includes total elapsed time and all splits in a plain text table.

## Reliability tips for track testing

- Mount camera stable on tripod.
- Keep virtual line where runner body fully crosses frame.
- Avoid strong backlight and excessive camera shake.
- Tune `--min-area` until only runners trigger crossings.
- Use `--cooldown` to prevent multiple counts per pass.

## Next-step enhancements (after MVP)

- Save event clips around each crossing.
- Add lap-distance context (100m/200m/etc.) and pace estimates.
- Add optional cloud/AI post-workout analysis.
