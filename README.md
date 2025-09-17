# s2t-mini — Speech‑to‑Text (Whisper) Starter

A tiny project that converts **audio → text** locally using [faster‑whisper] (a fast Whisper inference engine). Works on Windows, macOS, and Linux; CPU‑only by default, with optional GPU acceleration (CUDA/ROCm if available).

> You can use it two ways:
> 1) **CLI**: `python app.py --audio path/to/file.mp3`
> 2) **Web UI (Streamlit)**: `streamlit run streamlit_app.py` and upload your audio.

---

## 1) Prereqs

- **Python 3.9+**
- **FFmpeg** installed and on PATH  
  - Windows (choco): `choco install ffmpeg`  
  - macOS (brew): `brew install ffmpeg`  
  - Linux (Debian/Ubuntu): `sudo apt-get update && sudo apt-get install -y ffmpeg`

> If FFmpeg isn’t found, the script will still try, but some formats may fail to load—installing FFmpeg is recommended.

---

## 2) Setup

```bash
# create and activate virtual env
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# upgrade pip
python -m pip install --upgrade pip

# install dependencies (CPU)
pip install -r requirements.txt
```

### (Optional) GPU acceleration

If you have an NVIDIA GPU with CUDA, install a compatible PyTorch and then:
```bash
pip install "faster-whisper[av]"
```
faster‑whisper will automatically try to use the GPU when `--device cuda` is provided.

---

## 3) Quick start (CLI)

```bash
# basic usage (auto language detection, outputs .txt and .srt next to your audio)
python app.py --audio "path/to/audio.mp4"

# choose a model size (tiny | base | small | medium | large-v3)
python app.py --audio "meeting.mp4" --model small

# force device/cpu or gpu (cuda) and set compute dtype
python app.py --audio "meeting.mp4" --device cpu
python app.py --audio "meeting.mp4" --device cuda --compute-type float16

# diarization-ready timestamps in SRT (you can add speaker tags later)
python app.py --audio "meeting.mp4" --srt
```

Outputs:
- `meeting.transcript.txt` — plain text transcript
- `meeting.transcript.srt` — subtitle file with timestamps (if `--srt` used)

---

## 4) Web UI (Streamlit)

```bash
streamlit run streamlit_app.py
```
Then open the browser URL shown (usually http://localhost:8501), upload an audio file, and click **Transcribe**. You’ll see the transcript on‑screen and can download it as `.txt` or `.srt`.

---

## 5) Tips

- **Model choices**: `tiny/base/small/medium` are faster; `large-v3` is most accurate but heavy.
- **Week‑1 summaries**: After transcribing a meeting, you can paste the text into ChatGPT and ask for a structured summary (agenda, decisions, action items, week‑1 plan).  
- **Confidential audio**: This runs locally; no cloud calls.
- **Languages**: Auto‑detects speech language by default; you can force English with `--language en`.

---

## 6) License

MIT
