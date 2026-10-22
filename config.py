import json
import logging

DEFAULTS = {"model": "small"}

log = logging.getLogger("dictado")


def load_config(path):
    """Read user settings from a JSON file, falling back to defaults on any problem."""
    try:
        # utf-8-sig tolerates the BOM that Windows PowerShell 5.1 adds
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return dict(DEFAULTS)
    except (OSError, ValueError):
        log.warning("config.json inválido, usando valores por defecto")
        return dict(DEFAULTS)
    return {**DEFAULTS, **data} if isinstance(data, dict) else dict(DEFAULTS)
