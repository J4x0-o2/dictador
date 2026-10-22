def clean_transcript(segments):
    """Join Whisper segments into a single line with normalized spacing."""
    return " ".join(" ".join(segments).split())
