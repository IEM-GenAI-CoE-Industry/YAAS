# 🎬 Script Agent — YouTube Reels Pipeline

A multi-agent YouTube video production pipeline. The **Script Agent** sits between the Thumbnail Agent and the Video Generation Agent — it takes a thumbnail description and outputs a production-ready 10-second Reel timeline.

---

## Pipeline Overview

```
Thumbnail Agent  →  Script Agent  →  Video Generation Agent
 thumbnail.json  →  script_agent.py  →  timeline.json
```

---

## Project Structure

```
script_agent/
├── script_agent.py        # core agent
├── test_agent.py          # test runner
├── timeline.sample.json   # sample output for video gen agent
├── .env.example           # required environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourname/script_agent.git
cd script_agent
```

**2. Create a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
cp .env.example .env
# open .env and add your Mistral API key
```

`.env` contents:
```
MISTRAL_API_KEY=your_mistral_key_here
SCRIPT_AGENT_MODEL=mistral-large-latest
SCRIPT_AGENT_MAX_TOKENS=4096
```

---

## Usage

**File in → file out**
```bash
python script_agent.py --input thumbnail.json --output timeline.json
```

**File in → stdout**
```bash
python script_agent.py --input thumbnail.json
```

**Stdin → stdout (pipe mode)**
```bash
cat thumbnail.json | python script_agent.py
```

**Full pipeline pipe**
```bash
python thumbnail_agent.py | python script_agent.py | python video_gen_agent.py
```

**Import as a module**
```python
from script_agent import run_script_agent

timeline = run_script_agent(thumbnail_data)  # dict in, dict out
```

---

## Input Schema (from Thumbnail Agent)

```json
{
  "subject": {
    "type": "human | object",
    "description": "visual description",
    "expression": "facial expression",
    "pose": "body pose",
    "shot_type": "close-up | mid-shot | wide"
  },
  "background": {
    "style": "clean | blurred | realistic | studio",
    "clutter_level": "low | medium",
    "lighting": "soft studio | cinematic | natural"
  },
  "emotion_style": "excited | dramatic | professional | friendly | serious",
  "color_palette": {
    "primary": "#HEX",
    "secondary": "#HEX",
    "accent": "#HEX"
  },
  "composition": {
    "subject_position": "center | left | right",
    "depth": "shallow | medium"
  },
  "text": {
    "content": "max 6 words",
    "style": "bold | clean | dramatic"
  }
}
```

---

## Output Schema (for Video Generation Agent)

Sample output → [`timeline.sample.json`](timeline.sample.json)

```
video_meta
├── title
├── duration_seconds          → always 10
├── tone
├── target_audience
├── hook_type
├── music_track_suggestion
└── b_roll_suggestions[]

render_hints
├── aspect_ratio              → always 9:16
├── resolution                → 1080x1920
├── fps                       → 30
├── color_palette_primary
├── color_palette_secondary
├── color_palette_accent
└── font_style

timeline[]                    → exactly 3 scenes
├── scene_01  (00:00–00:03)   hook
├── scene_02  (00:03–00:07)   main_point
└── scene_03  (00:07–00:10)   cta
    ├── id, timestamp_start, timestamp_end, duration_seconds
    ├── shot
    │   ├── type              → camera setup
    │   ├── camera_movement
    │   └── framing_notes
    ├── voiceover
    │   ├── text              → send to TTS
    │   ├── tone
    │   ├── pace
    │   └── pause_after_seconds
    ├── visual_direction
    │   ├── on_screen_subject → what to render
    │   ├── background
    │   ├── lighting
    │   ├── color_grade
    │   ├── overlay_text
    │   └── overlay_style
    ├── audio
    │   ├── music_mood        → music layer
    │   ├── music_volume
    │   └── sfx
    └── transition_to_next    → between scenes
```

---

## Test

```bash
python test_agent.py
```

Expected output:
```
Scenes     : 3
Total time : 10s
Aspect     : 9:16
✅ PASS — Timeline is exactly 10 seconds!
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `MISTRAL_API_KEY` | ✅ yes | — | Your Mistral API key |
| `SCRIPT_AGENT_MODEL` | no | `mistral-large-latest` | Mistral model to use |
| `SCRIPT_AGENT_MAX_TOKENS` | no | `4096` | Max tokens for response |

---

## Agents in This Pipeline

| Agent | Repo | Input | Output |
|---|---|---|---|
| Thumbnail Agent | `thumbnail_agent/` | topic string | `thumbnail.json` |
| **Script Agent** | `script_agent/` ← you are here | `thumbnail.json` | `timeline.json` |
| Video Gen Agent | `video_gen_agent/` | `timeline.json` | `.mp4` |
| SEO Agent | `seo_agent/` | `timeline.json` | metadata JSON |

---

## Notes

- `.env` is gitignored — never commit your API key
- `timeline.json` is gitignored — generated files are not tracked
- `timeline.sample.json` is committed — use it as the contract with the video gen agent