import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from mouse_oscillator import MouseJitter, load_config


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Mouse Oscillator")
        self.config_path = "config.json"
        self.cfg = load_config(self.config_path)
        self.jitter: Optional[MouseJitter] = None
        self.enabled = False
        self._bound_key: Optional[str] = None
        self.var_amplitude = tk.IntVar(value=int(self.cfg.get("amplitude_pixels", 12)))
        self.var_frequency = tk.DoubleVar(value=float(self.cfg.get("frequency_hz", 20)))
        self.var_key = tk.StringVar(value=str(self.cfg.get("trigger_key", "x")))
        self.var_toggle = tk.BooleanVar(value=bool(self.cfg.get("toggle_mode", False)))
        self.status_var = tk.StringVar(value="idle")
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=12)
        frm.grid(column=0, row=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        ttk.Label(frm, text="Amplitude (px)").grid(column=0, row=0, sticky="w")
        amp_entry = ttk.Entry(frm, textvariable=self.var_amplitude, width=10)
        amp_entry.grid(column=1, row=0, sticky="ew")
        ttk.Label(frm, text="Frequency (Hz)").grid(column=0, row=1, sticky="w")
        freq_entry = ttk.Entry(frm, textvariable=self.var_frequency, width=10)
        freq_entry.grid(column=1, row=1, sticky="ew")
        ttk.Label(frm, text="Trigger Key").grid(column=0, row=2, sticky="w")
        key_entry = ttk.Entry(frm, textvariable=self.var_key, width=10)
        key_entry.grid(column=1, row=2, sticky="ew")
        toggle_chk = ttk.Checkbutton(frm, text="Toggle Mode", variable=self.var_toggle)
        toggle_chk.grid(column=0, row=3, columnspan=2, sticky="w")
        btn_row = ttk.Frame(frm)
        btn_row.grid(column=0, row=4, columnspan=2, pady=8, sticky="ew")
        start_btn = ttk.Button(btn_row, text="Start", command=self.on_start)
        start_btn.grid(column=0, row=0, padx=4)
        stop_btn = ttk.Button(btn_row, text="Stop", command=self.on_stop)
        stop_btn.grid(column=1, row=0, padx=4)
        apply_btn = ttk.Button(btn_row, text="Apply", command=self.on_apply)
        apply_btn.grid(column=2, row=0, padx=4)
        save_btn = ttk.Button(btn_row, text="Save Config", command=self.on_save)
        save_btn.grid(column=3, row=0, padx=4)
        load_btn = ttk.Button(btn_row, text="Load Config", command=self.on_load)
        load_btn.grid(column=4, row=0, padx=4)
        ttk.Label(frm, textvariable=self.status_var).grid(column=0, row=5, columnspan=2, sticky="w")

    def current_values(self):
        amp = max(1, int(self.var_amplitude.get()))
        freq = max(0.1, float(self.var_frequency.get()))
        key = (self.var_key.get() or "x").strip()[:1]
        tog = bool(self.var_toggle.get())
        return amp, freq, key, tog

    def on_start(self):
        amp, freq, key, tog = self.current_values()
        # Recreate jitter with current settings, do not start yet
        if self.jitter is not None:
            self.jitter.stop()
        self.jitter = MouseJitter(amp, freq, key, tog)
        # Bind Tk key events (window-focused). Avoids macOS event-tap crash.
        self._rebind_keys(key)
        self.enabled = True
        self.status_var.set(f"armed: hold '{key}' in window to jitter")

    def on_stop(self):
        if self.jitter is not None:
            self.jitter.stop()
        self._unbind_keys()
        self.enabled = False
        self.status_var.set("stopped")

    def on_apply(self):
        amp, freq, key, tog = self.current_values()
        # Apply new settings; if armed, recreate listener with new jitter
        if self.jitter is not None:
            self.jitter.stop()
        self.jitter = MouseJitter(amp, freq, key, tog)
        if self.enabled:
            self._rebind_keys(key)
            self.status_var.set(f"armed: hold '{key}' in window to jitter")
        else:
            self.status_var.set("idle")

    def on_save(self):
        amp, freq, key, tog = self.current_values()
        data = {
            "amplitude_pixels": amp,
            "frequency_hz": freq,
            "trigger_key": key,
            "toggle_mode": tog,
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.status_var.set("saved")

    def on_load(self):
        self.cfg = load_config(self.config_path)
        self.var_amplitude.set(int(self.cfg.get("amplitude_pixels", 12)))
        self.var_frequency.set(float(self.cfg.get("frequency_hz", 20)))
        self.var_key.set(str(self.cfg.get("trigger_key", "x")))
        self.var_toggle.set(bool(self.cfg.get("toggle_mode", False)))
        self.status_var.set("loaded")

    def on_close(self):
        if self.jitter is not None:
            self.jitter.stop()
        self._unbind_keys()
        self.root.destroy()

    def _rebind_keys(self, key: str):
        self._unbind_keys()
        self._bound_key = key
        self.root.bind(f"<KeyPress-{key}>", self._on_key_press)
        self.root.bind(f"<KeyRelease-{key}>", self._on_key_release)

    def _unbind_keys(self):
        if self._bound_key:
            try:
                self.root.unbind(f"<KeyPress-{self._bound_key}>")
                self.root.unbind(f"<KeyRelease-{self._bound_key}>")
            except Exception:
                pass
        self._bound_key = None

    def _on_key_press(self, event):
        if not self.enabled or self.jitter is None:
            return
        if self.jitter.toggle_mode:
            self.jitter.toggle()
        else:
            self.jitter.start()

    def _on_key_release(self, event):
        if not self.enabled or self.jitter is None:
            return
        if not self.jitter.toggle_mode:
            self.jitter.stop()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
