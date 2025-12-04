import argparse
import json
import os
import threading
import time
from typing import Optional

from pynput.mouse import Controller
from pynput.keyboard import Listener as KeyboardListener, Key, KeyCode

from oscillator import Oscillator


def load_config(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "amplitude_pixels": 12,
        "frequency_hz": 20,
        "trigger_key": "x",
        "toggle_mode": False,
    }


class MouseJitter:
    def __init__(self, amplitude: int, frequency_hz: float, trigger_key_char: str, toggle_mode: bool):
        self.mouse = Controller()
        self.amplitude = amplitude
        self.frequency_hz = frequency_hz
        self.trigger_key_char = trigger_key_char.lower()
        self.toggle_mode = toggle_mode
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._osc: Optional[Oscillator] = None
        self._start_time = 0.0
        self._last_offset = 0

    def _key_matches(self, key) -> bool:
        if isinstance(key, KeyCode):
            return key.char is not None and key.char.lower() == self.trigger_key_char
        return False

    def start(self):
        if self._running:
            return
        cx, cy = self.mouse.position
        self._osc = Oscillator(cy, self.amplitude, self.frequency_hz)
        self._start_time = time.time()
        self._last_offset = 0
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        self._last_offset = 0

    def toggle(self):
        if self._running:
            self.stop()
        else:
            self.start()

    def _run_loop(self):
        while self._running:
            t = time.time() - self._start_time
            x, current_y = self.mouse.position
            new_offset = self._osc.offset_at(t)
            baseline_y = current_y - self._last_offset
            y = baseline_y + new_offset
            self.mouse.position = (x, y)
            self._last_offset = new_offset
            time.sleep(max(0.0, 1.0 / (self.frequency_hz * 2)))

    def on_press(self, key):
        if not self._key_matches(key):
            return
        if self.toggle_mode:
            self.toggle()
        else:
            self.start()

    def on_release(self, key):
        if not self._key_matches(key):
            return
        if not self.toggle_mode:
            self.stop()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--amplitude", type=int)
    parser.add_argument("--frequency", type=float)
    parser.add_argument("--key", type=str)
    parser.add_argument("--toggle", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    cfg = load_config(args.config)
    amplitude = args.amplitude if args.amplitude is not None else cfg.get("amplitude_pixels", 12)
    frequency = args.frequency if args.frequency is not None else cfg.get("frequency_hz", 20)
    key_char = (args.key if args.key is not None else cfg.get("trigger_key", "x")).lower()
    toggle = args.toggle or bool(cfg.get("toggle_mode", False))
    jitter = MouseJitter(amplitude, frequency, key_char, toggle)
    with KeyboardListener(on_press=jitter.on_press, on_release=jitter.on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
