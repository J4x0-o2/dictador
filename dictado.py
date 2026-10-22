"""Local push-to-talk dictation for Windows.

Press the hotkey once to start recording, press it again to stop.
The transcript is pasted into the focused window. Enter is never pressed,
so you can review the text before sending it.

A tray icon shows the current state and offers Pause/Resume and Exit.
"""

import logging
import sys
import threading
import time
import winsound
from pathlib import Path

import keyboard
import numpy as np
import pyperclip
import pystray
import sounddevice as sd

from config import load_config
from icon import make_icon
from text import clean_transcript

HOTKEY = "ctrl+alt+space"
LANGUAGE = "es"
BEAM_SIZE = 3  # 1 = greedy (fastest); higher explores more candidates for accuracy
SAMPLE_RATE = 16000  # Whisper expects 16 kHz mono audio
LOG_FILE = Path(__file__).with_name("dictado.log")
CONFIG_FILE = Path(__file__).with_name("config.json")

handlers = [logging.FileHandler(LOG_FILE, encoding="utf-8")]
if sys.stdout is not None:  # None when launched with pythonw.exe (no console)
    sys.stdout.reconfigure(encoding="utf-8")
    handlers.append(logging.StreamHandler(sys.stdout))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=handlers)
log = logging.getLogger("dictado")


class Dictation:
    def __init__(self, model, on_state_change=lambda state: None):
        self.model = model
        self.on_state_change = on_state_change
        self.chunks = []
        self.stream = None
        self.paused = False
        self.lock = threading.Lock()

    def toggle(self):
        with self.lock:
            if self.paused:
                return
            if self.stream is None:
                self._start()
            else:
                audio = self._stop()
                threading.Thread(target=self._transcribe_and_paste, args=(audio,), daemon=True).start()

    def set_paused(self, paused):
        with self.lock:
            if paused and self.stream is not None:
                self._stop()  # discard the in-progress recording
            self.paused = paused
        log.info("Pausado" if paused else "Reanudado")
        self.on_state_change("paused" if paused else "idle")

    def _start(self):
        self.chunks = []
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=lambda data, *_: self.chunks.append(data.copy()),
        )
        self.stream.start()
        winsound.Beep(880, 120)
        self.on_state_change("recording")
        log.info("Grabando...")

    def _stop(self):
        self.stream.stop()
        self.stream.close()
        self.stream = None
        winsound.Beep(440, 120)
        self.on_state_change("idle")
        log.info("Transcribiendo...")
        if not self.chunks:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(self.chunks).flatten()

    def _transcribe_and_paste(self, audio):
        try:
            self._process(audio)
        except Exception:
            log.exception("Error al transcribir o pegar")

    def _process(self, audio):
        log.info("Audio capturado: %.1f s", audio.size / SAMPLE_RATE)
        if audio.size < SAMPLE_RATE * 0.3:  # ignore accidental taps
            log.info("Audio demasiado corto, ignorado.")
            return
        started = time.time()
        segments, _ = self.model.transcribe(audio, language=LANGUAGE, vad_filter=True, beam_size=BEAM_SIZE)
        text = clean_transcript(segment.text for segment in segments)
        log.info("Transcripción en %.1f s", time.time() - started)
        if not text:
            log.info("No se detectó voz.")
            return
        log.info(f"> {text}")
        self._paste(text)
        log.info("Texto pegado")

    @staticmethod
    def _paste(text):
        previous = pyperclip.paste()
        pyperclip.copy(text)
        keyboard.send("ctrl+v")
        time.sleep(0.2)  # give the target app time to read the clipboard
        pyperclip.copy(previous)


TITLES = {
    "loading": "Dictador: cargando modelo...",
    "idle": f"Dictador: listo ({HOTKEY})",
    "recording": "Dictador: grabando...",
    "paused": "Dictador: en pausa",
}


def main():
    tray = pystray.Icon("dictador", make_icon("loading"), TITLES["loading"])

    def show_state(state):
        tray.icon = make_icon(state)
        tray.title = TITLES[state]

    dictation = Dictation(model=None, on_state_change=show_state)

    def load_model(icon):
        icon.visible = True
        try:
            from faster_whisper import WhisperModel  # slow import, keep it off the startup path

            model_size = load_config(CONFIG_FILE)["model"]
            log.info(f"Cargando modelo '{model_size}' (la primera vez lo descarga)...")
            dictation.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            log.info("Micrófono: %s", sd.query_devices(kind="input")["name"])
            keyboard.add_hotkey(HOTKEY, dictation.toggle)
            show_state("idle")
            log.info(f"Listo. Presioná {HOTKEY} para empezar/terminar.")
        except Exception:
            log.exception("No se pudo iniciar")
            icon.stop()

    def exit_app(icon, _item):
        log.info("Saliendo")
        keyboard.unhook_all()
        icon.stop()

    tray.menu = pystray.Menu(
        pystray.MenuItem(
            lambda _item: "Reanudar" if dictation.paused else "Pausar",
            lambda _icon, _item: dictation.set_paused(not dictation.paused),
        ),
        pystray.MenuItem("Salir", exit_app),
    )
    tray.run(setup=load_model)


if __name__ == "__main__":
    main()
