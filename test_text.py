from text import clean_transcript


def test_joins_segments_and_trims_whitespace():
    assert clean_transcript(["  Hola, ", " ¿cómo estás?  "]) == "Hola, ¿cómo estás?"


def test_collapses_inner_whitespace():
    assert clean_transcript(["uno   dos", "tres"]) == "uno dos tres"


def test_empty_or_silent_input_returns_empty_string():
    assert clean_transcript([]) == ""
    assert clean_transcript(["   ", ""]) == ""
