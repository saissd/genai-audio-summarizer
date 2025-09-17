from transformers import pipeline
import pathlib

# load summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# input transcript file (replace with your transcript filename)
transcript_path = pathlib.Path("record1.transcript.txt")
text = transcript_path.read_text(encoding="utf-8")

# split into chunks (BART can handle ~1024 tokens)
max_chunk = 800
chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]

# summarize each chunk
summaries = []
for chunk in chunks:
    result = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
    summaries.append(result[0]['summary_text'])

# combine summaries into bullet points
final_summary = "📌 Meeting Summary\n\n" + "\n- " + "\n- ".join(summaries)

# save to file
summary_path = transcript_path.with_suffix(".summary.txt")
summary_path.write_text(final_summary, encoding="utf-8")

print("✅ Summary saved to", summary_path)
print()
print(final_summary)
