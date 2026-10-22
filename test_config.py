from config import DEFAULTS, load_config


def test_missing_file_returns_defaults(tmp_path):
    assert load_config(tmp_path / "config.json") == DEFAULTS


def test_file_overrides_model(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"model": "medium"}', encoding="utf-8")
    assert load_config(path)["model"] == "medium"


def test_accepts_utf8_bom_written_by_powershell(tmp_path):
    path = tmp_path / "config.json"
    path.write_bytes(b'\xef\xbb\xbf{"model": "base"}')
    assert load_config(path)["model"] == "base"


def test_corrupt_file_falls_back_to_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{not json", encoding="utf-8")
    assert load_config(path) == DEFAULTS


def test_default_model_is_small():
    assert DEFAULTS["model"] == "small"
