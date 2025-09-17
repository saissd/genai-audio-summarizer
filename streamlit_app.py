import io
from pathlib import Path
import tempfile
import streamlit as st
from faster_whisper import WhisperModel
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript
import yt_dlp   # ✅ replacing pytube for reliability

st.set_page_config(page_title="s2t-mini", page_icon="🎙️", layout="centered")
st.title("🎙️ s2t-mini — Speech → Text & Summary")

with st.expander("Settings", expanded=False):
    model_size = st.selectbox("Whisper model", ["tiny","base","small","medium","large-v3"], index=2)
    device = st.selectbox("Device", ["cpu","cuda"], index=0)
    compute_type = st.selectbox("Compute type", ["int8","float16","float32"], index=0)
    force_lang = st.text_input("Force language (leave blank for auto)", value="")

tabs = st.tabs(["Upload audio/video", "YouTube URL"])

status = st.empty()

# ----- Common helpers -----
def format_ts(seconds: float) -> str:
    ms = int(round(seconds * 1000.0))
    hrs, ms = divmod(ms, 3600 * 1000)
    mins, ms = divmod(ms, 60 * 1000)
    secs, ms = divmod(ms, 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

def summarize_text(long_text: str) -> str:
    # chunk & summarize with BART (use distilbart for speed)
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    chunks = [long_text[i:i+800] for i in range(0, len(long_text), 800)] or [long_text]
    bullets = []
    for ch in chunks:
        result = summarizer(ch, max_length=150, min_length=50, do_sample=False)
        bullets.append(result[0]["summary_text"])
    return "📌 Meeting Summary\n\n" + "\n- " + "\n- ".join(bullets)

def transcribe_file(path: Path):
    model = WhisperModel(model_size_or_path=model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(str(path), language=(force_lang or None), vad_filter=True)
    text_buf = io.StringIO()
    srt_buf = io.StringIO()
    idx = 1
    for seg in segments:
        text_buf.write(seg.text)
        srt_buf.write(f"{idx}\n{format_ts(seg.start)} --> {format_ts(seg.end)}\n{seg.text.strip()}\n\n")
        idx += 1
    transcript = text_buf.getvalue().strip()
    srt_text = srt_buf.getvalue()
    return transcript, srt_text, info

def yt_id_from_url(url: str) -> str | None:
    import re
    m = re.search(r"(?:v=|/shorts/|/live/|youtu\.be/)([A-Za-z0-9_-]{6,})", url)
    return m.group(1) if m else None

# ----- Tab 1: Upload -----
with tabs[0]:
    uploaded = st.file_uploader("Upload an audio/video file", type=["mp3","wav","m4a","mp4","mov","aac","flac","ogg","webm"])
    c1, c2 = st.columns(2)
    run_upload = c1.button("Transcribe & Summarize")
    write_srt = c2.checkbox("Generate .srt file", value=True)

    if run_upload:
        if not uploaded:
            st.warning("Please upload a file first.")
        else:
            status.info("Transcribing…")
            tmp_path = Path(tempfile.gettempdir()) / ("temp_" + uploaded.name)
            tmp_path.write_bytes(uploaded.read())
            transcript, srt_text, info = transcribe_file(tmp_path)

            st.subheader("📝 Transcript")
            st.text_area("Transcript", transcript, height=300)
            st.caption(f"Detected language: {info.language} (prob={info.language_probability:.2f})")

            status.info("Summarizing…")
            summary = summarize_text(transcript)
            st.subheader("📌 Auto Summary")
            st.write(summary)

            # Downloads
            st.download_button("Download transcript (.txt)", data=transcript, file_name=f"{uploaded.name}.transcript.txt")
            if write_srt:
                st.download_button("Download subtitles (.srt)", data=srt_text, file_name=f"{uploaded.name}.transcript.srt")
            st.download_button("Download summary (.txt)", data=summary, file_name=f"{uploaded.name}.summary.txt")

            status.success("Done ✅")

# ----- Tab 2: YouTube -----
with tabs[1]:
    yt_url = st.text_input("Paste a YouTube link", placeholder="https://www.youtube.com/watch?v=...")
    c3, c4 = st.columns(2)
    run_yt = c3.button("Summarize YouTube")
    prefer_transcript = c4.checkbox("Prefer official transcript if available (faster)", value=True)

    if run_yt:
        if not yt_url.strip():
            st.warning("Please paste a YouTube URL.")
        else:
            vid = yt_id_from_url(yt_url)
            if not vid:
                st.error("Could not parse video ID from the URL.")
            else:
                transcript = None
                # 1) Try official transcript first
                if prefer_transcript:
                    status.info("Trying to fetch official YouTube transcript…")
                    try:
                        data = YouTubeTranscriptApi.get_transcript(vid, languages=["en"])
                        transcript = " ".join(item["text"] for item in data)
                        detected = "Source: Official YouTube transcript"
                    except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript, Exception):
                        transcript = None

                # 2) Fallback: download audio with yt-dlp and transcribe locally
                if not transcript or len(transcript.strip()) < 20:
                    status.info("No transcript found. Downloading audio and transcribing locally… (this may take a bit)")
                    try:
                        out_file = Path(tempfile.gettempdir()) / f"yt_{vid}.m4a"
                        ydl_opts = {
                            "format": "bestaudio/best",
                            "outtmpl": str(out_file),
                            "quiet": True,
                            "noprogress": True,
                        }
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([yt_url])
                        transcript, srt_text, info = transcribe_file(out_file)
                        detected = f"Detected language: {info.language} (prob={info.language_probability:.2f})"
                    except Exception as e:
                        st.error(f"Download/transcription failed: {e}")
                        transcript = None
                        detected = None

                if not transcript:
                    st.error("Could not get a transcript for this video.")
                else:
                    st.subheader("📝 Transcript")
                    st.text_area("Transcript", transcript, height=300)
                    if detected:
                        st.caption(detected)

                    status.info("Summarizing…")
                    summary = summarize_text(transcript)

                    st.subheader("📌 Auto Summary")
                    st.write(summary)

                    # Downloads
                    title_safe = (vid or "youtube_video")
                    st.download_button("Download transcript (.txt)", data=transcript, file_name=f"{title_safe}.transcript.txt")
                    st.download_button("Download summary (.txt)", data=summary, file_name=f"{title_safe}.summary.txt")

                    status.success("Done ✅")
