# CoachMe GUI Prototype (CustomTkinter)

This project now provides a **multi-page desktop GUI flow** for the Raspberry Pi track coach prototype using **mock/demo data** (no live camera timing yet).

## Current scope

Implemented pages:

1. Athlete Input Page
2. Pre-Workout Summary Page
3. Workout Page with **live camera split tracking**
4. Final Summary Page with split review, placeholders, and export

## Project structure

- `main.py`
- `ui/app.py`
- `ui/pages/input_page.py`
- `ui/pages/pre_workout_page.py`
- `ui/pages/workout_page.py`
- `ui/pages/final_summary_page.py`
- `models/runner_profile.py`
- `models/workout_result.py`
- `services/summary_generator.py`
- `services/export_service.py`

## Features implemented

- Cohesive no-API workflow: input -> live workout tracking -> final summary/export
- Athlete profile capture:
  - event specialization checkboxes (`100m`, `200m`, `400m`, `800m`, `1600m`, `3200m`) with up to 2 selections
  - weight, biological sex, age, height
  - PR inputs
  - workout description textbox
  - `No prior workout plan` checkbox disables workout textbox
- RETURN TO BEGINNING resets all first-page fields to defaults
- Pre-workout summary with friendly greeting
- Workout page live split table with status indicators:
  - `▲` red = slower than target pace
  - `▼` yellow = too much faster than target pace
  - `✓` green = on pace
- Final summary page:
  - rule-based AI-style summary placeholder
  - collapsible split review
  - future workout suggestion
  - following-day recovery/training suggestion
- Download summary to `.txt` with athlete profile + workout description + split table

## Setup (Raspberry Pi / Linux)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-tk
```

Create a virtual environment and install Python packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 main.py
```

## Export output

When you click **DOWNLOAD SUMMARY**, the app writes a text file to:

- `results/coachme_summary_<timestamp>.txt`

## Notes

- This version intentionally uses **no AI API**. Summary/advice text is placeholder/rule-based so an API can be added later without breaking the current flow.

## Live split tracking integration

The GUI workout page is now connected to `coachme.py` in real time:

- Clicking **START** launches split tracking in a background thread via `services/split_tracking_service.py`.
- `coachme.py` exposes a callable `run_split_tracking(...)` function with an `on_split_detected` callback.
- Each detected split is pushed back to the GUI using thread-safe `app.after(...)` updates, so the table updates live without freezing the UI.
- Clicking **END WORKOUT** stops tracking safely, keeps txt/csv save behavior, and passes recorded splits to the final summary page.
