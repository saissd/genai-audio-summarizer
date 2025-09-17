# genai-audio-summarizer

A simple, local-first app to transcribe audio/video (or YouTube links) and generate a bullet-point summary.

Transcription: faster-whisper (Whisper via CTranslate2)

Summarization: DistilBART (sshleifer/distilbart-cnn-12-6)

YouTube: youtube-transcript-api (official transcript) → fallback to yt-dlp (download audio)

UI: Streamlit

No paid APIs required. Runs on CPU by default. Great for meeting notes, lectures, onboarding sessions, etc.

✨ Features

Upload audio/video files (mp3/wav/m4a/mp4/…)

Paste a YouTube URL

Try official transcript (fast)

If missing → download audio with yt-dlp → transcribe locally

Automatic summary (bullet points), plus download buttons for .txt and .srt

Works on Windows/macOS/Linux

⚡ Quick Start
# 1) Create and activate a venv
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

# 2) Upgrade pip
python -m pip install --upgrade pip

# 3) Install requirements (CPU-friendly)
pip install -r requirements.txt

# 4) (Windows) Ensure ffmpeg is installed (for yt-dlp)
# choco install ffmpeg

# 5) Run the app
streamlit run streamlit_app.py


Open the local URL shown (usually http://localhost:8501
).

📦 Requirements

requirements.txt (suggested)

streamlit==1.38.0
faster-whisper==1.0.3
transformers==4.44.2
sentencepiece==0.2.0
youtube-transcript-api==0.6.2
yt-dlp==2024.08.06
faiss-cpu==1.8.0   # optional; kept if you add RAG later
torch==2.2.2+cpu ; platform_system=="Windows"
torchvision==0.17.2+cpu ; platform_system=="Windows"
torchaudio==2.2.2+cpu ; platform_system=="Windows"
numpy<2


If pip complains about torch wheels on Windows, install via:

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

🖥️ Usage
Tab 1 — Upload audio/video

Choose a Whisper model in Settings (start with tiny for speed).

Upload file and click Transcribe & Summarize.

Download Transcript (.txt), Subtitles (.srt), and Summary (.txt).

Tab 2 — YouTube URL

Paste a full YouTube link.

Keep Prefer official transcript checked for speed.

If no official transcript, the app uses yt-dlp to fetch audio (shows a progress bar) and then transcribes.

First run may take a few minutes to download models. This only happens once.

🛠️ Troubleshooting

1) “None of PyTorch/TensorFlow/Flax found” / NameError: torch is not defined
Install CPU torch wheels:

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu


2) NumPy 2.x errors (e.g., “A module compiled with NumPy 1.x cannot run in 2.x”)

pip uninstall -y numpy
pip install "numpy<2"


3) yt-dlp hangs at “Downloading audio…”

Install ffmpeg and restart terminal (choco install ffmpeg on Windows).

Some videos require cookies: in the code we enable cookiesfrombrowser=("chrome",). Keep Chrome open/signed in.

Try another video to rule out regional/age restrictions.

4) Slow on first run

Models download on first use. Use Whisper = tiny to test.

Summarizer can be switched to facebook/bart-large-cnn for higher quality (slower) if you prefer.

5) Syntax/encoding issues on Windows

Use UTF-8 in your editor.

Run PowerShell as user (not admin) unless needed for choco.

🗂️ Project Structure
s2t-mini/
  streamlit_app.py       # UI, YouTube + Upload tabs, ASR + Summary pipeline
  requirements.txt
  README.md
  .gitignore


.gitignore (suggested)

.venv/
__pycache__/
*.transcript.txt
*.summary.txt
*.srt
*.m4a
*.mp4
.DS_Store

🔒 Notes on Privacy & Use

This app runs locally; transcripts/summaries are stored on your machine.

Respect website terms of service when downloading content. Use YouTube transcripts where available.

🙏 Acknowledgements

OpenAI Whisper via faster-whisper / CTranslate2

Hugging Face Transformers (DistilBART)

youtube-transcript-api, yt-dlp

Streamlit

🧪 Roadmap (optional)

Chaptered summaries with timestamps

Batch mode for multiple YouTube links

RAG (retrieve from PDFs/Docs to enrich summaries)

Speaker diarization for meetings

Dockerfile + GitHub Actions CI
