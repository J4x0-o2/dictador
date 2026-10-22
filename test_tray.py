from icon import COLORS, make_icon


def test_icon_is_square_rgba():
    image = make_icon("idle")
    assert image.size == (64, 64)
    assert image.mode == "RGBA"


def test_each_state_uses_its_own_color():
    for state, color in COLORS.items():
        assert make_icon(state).getpixel((32, 20))[:3] == color


def test_hotkey_is_ignored_while_paused(monkeypatch):
    import dictado

    dictation = dictado.Dictation(model=None)
    monkeypatch.setattr(dictation, "_start", lambda: (_ for _ in ()).throw(AssertionError("must not record")))
    dictation.paused = True
    dictation.toggle()
    assert dictation.stream is None
