import argparse
import sys
from pathlib import Path
from datetime import timedelta

from faster_whisper import WhisperModel

def format_timestamp(seconds: float) -> str:
    """Return SRT timestamp format HH:MM:SS,mmm from seconds."""
    ms = int(round(seconds * 1000.0))
    hrs, ms = divmod(ms, 3600 * 1000)
    mins, ms = divmod(ms, 60 * 1000)
    secs, ms = divmod(ms, 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

def write_srt(segments, out_path: Path):
    with out_path.open("w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = format_timestamp(seg.start)
            end = format_timestamp(seg.end)
            text = seg.text.strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

def main():
    parser = argparse.ArgumentParser(description="Audio → Text with faster-whisper")
    parser.add_argument("--audio", required=True, help="Path to audio/video file")
    parser.add_argument("--model", default="small", help="Whisper model size (tiny|base|small|medium|large-v3)")
    parser.add_argument("--device", default="cpu", help="Device: cpu or cuda")
    parser.add_argument("--compute-type", default="int8", help="Compute type: int8, float16, float32")
    parser.add_argument("--language", default=None, help="Force language code (e.g., en); default: auto detect")
    parser.add_argument("--srt", action="store_true", help="Also write an SRT subtitle file")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"[error] File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[info] Loading model: {args.model} (device={args.device}, compute={getattr(args, 'compute_type', 'int8')})")

    # Workaround for hyphenated arg name in print above
    compute_type = getattr(args, "compute_type", "int8")

    model = WhisperModel(model_size_or_path=args.model, device=args.device, compute_type=compute_type)

    print("[info] Transcribing...")
    segments, info = model.transcribe(str(audio_path), language=args.language, vad_filter=True)

    # Accumulate text
    full_text = []
    segs = []
    for seg in segments:
        segs.append(seg)
        full_text.append(seg.text)

    text_out = audio_path.with_suffix(".transcript.txt")
    text_out.write_text("".join(full_text).strip(), encoding="utf-8")
    print(f"[ok] Wrote text → {text_out.name}")

    if args.srt:
        srt_out = audio_path.with_suffix(".transcript.srt")
        write_srt(segs, srt_out)
        print(f"[ok] Wrote subtitles → {srt_out.name}")

    # Print detected language info
    print(f"[info] Detected language: {info.language} (prob={info.language_probability:.2f})")

if __name__ == "__main__":
    main()
