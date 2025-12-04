import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import multiprocessing as mp
import queue as queue_mod

from mouse_oscillator import MouseJitter, load_config


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("鼠标上下振动工具")
        self.config_path = "config.json"
        self.cfg = load_config(self.config_path)
        self.jitter: Optional[MouseJitter] = None
        self.enabled = False
        self._bound_key: Optional[str] = None
        self.kb_proc: Optional[mp.Process] = None
        self.kb_queue: Optional[mp.Queue] = None
        self.var_amplitude = tk.IntVar(value=int(self.cfg.get("amplitude_pixels", 12)))
        self.var_frequency = tk.DoubleVar(value=float(self.cfg.get("frequency_hz", 20)))
        self.var_key = tk.StringVar(value=str(self.cfg.get("trigger_key", "x")))
        self.var_toggle = tk.BooleanVar(value=bool(self.cfg.get("toggle_mode", False)))
        self.status_var = tk.StringVar(value="空闲")
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=12)
        frm.grid(column=0, row=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        ttk.Label(frm, text="振幅（像素）").grid(column=0, row=0, sticky="w")
        amp_entry = ttk.Entry(frm, textvariable=self.var_amplitude, width=10)
        amp_entry.grid(column=1, row=0, sticky="ew")
        ttk.Label(frm, text="频率（Hz）").grid(column=0, row=1, sticky="w")
        freq_entry = ttk.Entry(frm, textvariable=self.var_frequency, width=10)
        freq_entry.grid(column=1, row=1, sticky="ew")
        ttk.Label(frm, text="触发键").grid(column=0, row=2, sticky="w")
        key_entry = ttk.Entry(frm, textvariable=self.var_key, width=10)
        key_entry.grid(column=1, row=2, sticky="ew")
        toggle_chk = ttk.Checkbutton(frm, text="切换模式", variable=self.var_toggle)
        toggle_chk.grid(column=0, row=3, columnspan=2, sticky="w")
        btn_row = ttk.Frame(frm)
        btn_row.grid(column=0, row=4, columnspan=2, pady=8, sticky="ew")
        start_btn = ttk.Button(btn_row, text="开始武装", command=self.on_start)
        start_btn.grid(column=0, row=0, padx=4)
        stop_btn = ttk.Button(btn_row, text="解除武装", command=self.on_stop)
        stop_btn.grid(column=1, row=0, padx=4)
        apply_btn = ttk.Button(btn_row, text="应用参数", command=self.on_apply)
        apply_btn.grid(column=2, row=0, padx=4)
        save_btn = ttk.Button(btn_row, text="保存配置", command=self.on_save)
        save_btn.grid(column=3, row=0, padx=4)
        load_btn = ttk.Button(btn_row, text="加载配置", command=self.on_load)
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
        # Start global key listener in a separate process to avoid Tk/event-tap conflict
        self._start_global_listener(key)
        self.enabled = True
        self.status_var.set(f"已武装：按住 '{key}' 全局抖动")

    def on_stop(self):
        if self.jitter is not None:
            self.jitter.stop()
        self._stop_global_listener()
        self.enabled = False
        self.status_var.set("已停止")

    def on_apply(self):
        amp, freq, key, tog = self.current_values()
        # Apply new settings; if armed, recreate listener with new jitter
        if self.jitter is not None:
            self.jitter.stop()
        self.jitter = MouseJitter(amp, freq, key, tog)
        if self.enabled:
            self._start_global_listener(key)
            self.status_var.set(f"已武装：按住 '{key}' 全局抖动")
        else:
            self.status_var.set("空闲")

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
        self.status_var.set("已保存")

    def on_load(self):
        self.cfg = load_config(self.config_path)
        self.var_amplitude.set(int(self.cfg.get("amplitude_pixels", 12)))
        self.var_frequency.set(float(self.cfg.get("frequency_hz", 20)))
        self.var_key.set(str(self.cfg.get("trigger_key", "x")))
        self.var_toggle.set(bool(self.cfg.get("toggle_mode", False)))
        self.status_var.set("已加载")

    def on_close(self):
        if self.jitter is not None:
            self.jitter.stop()
        self._stop_global_listener()
        self.root.destroy()

    def _start_global_listener(self, key: str):
        self._stop_global_listener()
        self.kb_queue = mp.Queue()
        try:
            self.kb_proc = mp.Process(target=kb_child, args=(key.lower(), self.kb_queue), daemon=True)
            self.kb_proc.start()
            self.root.after(20, self._poll_keyboard_queue)
        except Exception as e:
            self.kb_proc = None
            self.kb_queue = None
            messagebox.showerror(
                "需要权限",
                "启动全局快捷键监听失败：请到 系统设置→隐私与安全→输入监控 为终端/IDE或Python授权。\n\n错误：" + str(e),
            )

    def _stop_global_listener(self):
        if self.kb_proc is not None:
            try:
                self.kb_proc.terminate()
            except Exception:
                pass
        self.kb_proc = None
        self.kb_queue = None

    def _poll_keyboard_queue(self):
        if self.kb_queue is None:
            return
        try:
            while True:
                ev = self.kb_queue.get_nowait()
                if ev == "press":
                    if self.jitter and self.enabled:
                        if self.jitter.toggle_mode:
                            self.jitter.toggle()
                        else:
                            self.jitter.start()
                elif ev == "release":
                    if self.jitter and self.enabled and not self.jitter.toggle_mode:
                        self.jitter.stop()
        except queue_mod.Empty:
            pass
        if self.enabled:
            self.root.after(20, self._poll_keyboard_queue)


def kb_child(key_char: str, q: mp.Queue):
    from pynput.keyboard import Listener, KeyCode

    def _match(k):
        try:
            return isinstance(k, KeyCode) and k.char is not None and k.char.lower() == key_char
        except Exception:
            return False

    def on_press(k):
        if _match(k):
            q.put("press")

    def on_release(k):
        if _match(k):
            q.put("release")

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
