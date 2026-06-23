"""Thought-capture overlay — a Win+H-style floating mic panel.

A push-a-button front end for the personal thought-capture pipeline. A small,
always-on-top, borderless panel: tap the mic to start, tap again to stop. On
stop it transcribes the whole session in one coherent Parakeet pass (D27),
applies the exact mis-hear corrections, writes the Markdown note to the vault,
indexes it (D28/D29), and opens the note. No terminal, no Ctrl-C, no cd.

This is a UI shell only. Every load-bearing step is the SAME function the CLI
(tools/capture_session.py) calls — dual_capture (mic-only), decode_chunked,
apply_corrections, MarkdownVaultTranscriptSink.write_session_note, ingest_capture,
plus crash recovery. The overlay replaces the CLI's "loop until Ctrl-C" with a
Stop button backed by the UI event loop; nothing else about the pipeline changes.

Usage:
    pythonw tools/capture_overlay.py        # the floating panel (no console)
    python  tools/capture_overlay.py        # same, with a console for logs
    python  tools/capture_overlay.py --smoke # wiring proof: import + construct, no mic
"""
from __future__ import annotations

import argparse
import ctypes
import os
import queue
import sys
import threading
import time
import uuid
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# --- palette (matches the Win+H dark panel) --------------------------------
BG = "#1e1f22"          # panel fill
BG_KEY = "#010203"      # transparent color key -> rounded corners
FG = "#e6e6e6"
MUTED = "#8a8d93"
MIC_IDLE = "#3a86ff"    # blue idle mic
MIC_REC = "#ff453a"     # red while recording
RING = "#2a2c30"


def already_running() -> bool:
    """True if another overlay instance already holds the named mutex, so the
    hotkey can't stack panels on repeated presses. The handle is intentionally
    left open for the process lifetime (that is what holds the mutex). Native
    Win32 via ctypes; best-effort — a guard failure must never block launch."""
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateMutexW(None, False, "Local\\ShowerThoughtsOverlay")
        return kernel32.GetLastError() == 183  # ERROR_ALREADY_EXISTS
    except Exception:  # noqa: BLE001
        return False


def active_work_area() -> "tuple[int, int, int, int] | None":
    """Work area (taskbar excluded) of the monitor under the mouse cursor, as
    (left, top, right, bottom). Native Win32 via ctypes (no dependency); returns
    None on any failure so the caller falls back to the primary screen."""
    class _MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", wintypes.RECT),
            ("rcWork", wintypes.RECT),
            ("dwFlags", wintypes.DWORD),
        ]

    try:
        user32 = ctypes.windll.user32
        pt = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        hmon = user32.MonitorFromPoint(pt, 2)  # MONITOR_DEFAULTTONEAREST
        mi = _MONITORINFO()
        mi.cbSize = ctypes.sizeof(_MONITORINFO)
        if user32.GetMonitorInfoW(hmon, ctypes.byref(mi)):
            r = mi.rcWork
            return r.left, r.top, r.right, r.bottom
    except Exception:  # noqa: BLE001 - positioning is cosmetic; never block launch
        pass
    return None


class CaptureController:
    """Owns the audio worker + pipeline. Talks to the UI only through `events`
    (a thread-safe queue the UI drains on the main thread). Never touches Tk."""

    def __init__(self, events: "queue.Queue[tuple]"):
        self.events = events
        self.stt = None
        self._cap = None
        self._recorder = None
        self._sink = None
        self._vault = "."
        self._session_id = ""
        self._packets = 0
        self._stopping = False

    # -- model warm-load (so the first record is instant) -------------------
    def warm_load(self) -> None:
        def _load():
            try:
                from audio.stt_engine import ParakeetEngine
                from audio.transcript_sink import MarkdownVaultTranscriptSink, vault_path

                self.stt = ParakeetEngine()
                self.stt.decode(b"\x00\x00" * 1600, 16000)  # one-time model load
                self._sink = MarkdownVaultTranscriptSink(vault_path())
                self._vault = vault_path()
                self._recover_orphans()
                self.events.put(("ready", str(self._vault)))
            except Exception as exc:  # noqa: BLE001 - surface to the panel, never crash it
                self.events.put(("fatal", f"{type(exc).__name__}: {exc}"))

        threading.Thread(target=_load, daemon=True).start()

    def _recover_orphans(self) -> None:
        # A capture interrupted by a hard close left a .pcm; turn it into a note
        # before the new session. Mirrors capture_session.py.
        from thought_capture.recovery import orphans, recover

        for orphan in orphans():
            try:
                note = recover(orphan, self.stt, self._sink)
                if note:
                    self.events.put(("status", "recovered an interrupted capture"))
            except Exception:  # noqa: BLE001 - leave the .pcm to retry next run
                pass

    # -- record -------------------------------------------------------------
    def start(self) -> None:
        from audio import dual_capture
        from thought_capture.recovery import IncrementalAudioRecorder

        session_id = str(uuid.uuid4())
        self._recorder = IncrementalAudioRecorder(session_id)
        self._session_id = session_id
        self._packets = 0
        self._stopping = False

        def on_packet(p) -> None:
            if p.source_stream == "operator_mic":
                self._recorder.write(p.pcm)
                self._packets += 1

        self._cap = dual_capture.DualStreamCapturer(
            on_packet=on_packet, clock_ms=lambda: int(time.time() * 1000)
        )
        started = self._cap.start(mic_only=True)
        if "operator_mic" not in started:
            self._recorder.discard()
            self.events.put(("error", "No microphone. Check Windows Sound input device."))
            return
        self.events.put(("recording", session_id))

    def stop(self) -> None:
        """Stop capture and run the pipeline on a worker thread (decode + enrich
        take seconds; never block the UI thread)."""
        if self._stopping:
            return
        self._stopping = True
        threading.Thread(target=self._finish, daemon=True).start()

    def abort(self) -> None:
        """Panel closed mid-capture: stop the mic but LEAVE the .pcm on disk so
        the next launch recovers it into a note. Conditional cleanup
        across two UI events -> a `try/finally`-class boundary, not a `with`
        block (dev/05). Best-effort: a shutdown path must never raise."""
        try:
            if self._cap is not None:
                self._cap.stop()  # joins capture thread; .pcm stays for recovery
        except Exception:  # noqa: BLE001 - best-effort on shutdown
            pass

    def _finish(self) -> None:
        try:
            self._cap.stop()  # joins capture thread -> .pcm holds full session
            if self._packets == 0:
                self._recorder.discard()
                self.events.put(("error", "No audio captured. Is the mic the default input?"))
                return
            secs = self._packets // 10
            self.events.put(("status", f"transcribing ~{secs}s ..."))

            from audio.stt_engine import decode_chunked
            from thought_capture.correct import apply_corrections
            from thought_capture.vocab import load_corrections

            text = decode_chunked(self.stt, self._recorder.read_all(), 16000)
            if not text:
                failed = self._recorder.preserve_failed()
                self.events.put(("error", f"Transcribed empty (too quiet?). Saved: {failed}"))
                return
            text, _fixes = apply_corrections(text, load_corrections())
            path = self._sink.write_session_note(self._session_id, text)
            self._recorder.discard()  # note is the floor; drop .pcm before enrich
            self.events.put(("status", "indexing ..."))

            from thought_capture.library import ingest_capture

            try:
                ingest_capture(path, text)
            except Exception:  # noqa: BLE001 - transcript note is safe; enrich is best-effort
                pass
            self.events.put(("done", str(path)))
        except Exception as exc:  # noqa: BLE001 - surface to the panel, never crash it
            self.events.put(("error", f"{type(exc).__name__}: {exc}"))


# --------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------
def run_ui() -> int:
    import tkinter as tk

    if already_running():
        return 0  # the hotkey was pressed while a panel is open; don't stack

    events: "queue.Queue[tuple]" = queue.Queue()
    ctl = CaptureController(events)

    root = tk.Tk()
    root.overrideredirect(True)            # borderless
    root.attributes("-topmost", True)      # always on top
    W, H = 260, 132
    area = active_work_area()
    if area:
        left, top, right, bottom = area
        x = left + (right - left - W) // 2
        y = bottom - H - 16            # 16px above the taskbar, like Win+H
    else:
        x = (root.winfo_screenwidth() - W) // 2
        y = root.winfo_screenheight() - H - 60
    root.geometry(f"{W}x{H}+{x}+{y}")
    root.configure(bg=BG)

    cv = tk.Canvas(root, width=W, height=H, bg=BG, highlightthickness=1,
                   highlightbackground=RING)
    cv.pack(fill="both", expand=True)

    def rrect(x1, y1, x2, y2, r, **kw):
        cv.create_polygon(
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2,
            x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1, smooth=True, **kw,
        )

    rrect(1, 1, W-1, H-1, 18, fill=BG, outline=RING)

    # drag handle (top pill) + close (X)
    cv.create_line(W/2-16, 12, W/2+16, 12, fill=MUTED, width=3, capstyle="round")
    x_id = cv.create_text(W-16, 14, text="✕", fill=MUTED, font=("Segoe UI", 11))

    # gear (open vault) + help
    gear_id = cv.create_text(26, H-20, text="⚙", fill=MUTED, font=("Segoe UI", 14))
    help_id = cv.create_text(W-26, H-20, text="?", fill=MUTED, font=("Segoe UI", 13, "bold"))

    # central mic button
    cx, cy, rad = W/2, 62, 26
    ring_id = cv.create_oval(cx-rad-6, cy-rad-6, cx+rad+6, cy+rad+6, outline=RING, width=2)
    btn_id = cv.create_oval(cx-rad, cy-rad, cx+rad, cy+rad, fill=MIC_IDLE, outline="")
    mic_id = cv.create_text(cx, cy, text="\U0001F3A4", font=("Segoe UI Emoji", 18))
    status_id = cv.create_text(W/2, H-20, text="loading model ...", fill=MUTED,
                               font=("Segoe UI", 9))

    state = {"mode": "loading", "t0": 0.0, "pulse": False}

    def set_status(txt, color=MUTED):
        cv.itemconfigure(status_id, text=txt, fill=color)

    def set_mic(color):
        cv.itemconfigure(btn_id, fill=color)

    def set_mic_glyph(glyph):
        cv.itemconfigure(mic_id, text=glyph)

    # -- drag the panel; suppress the click that ends a drag ----------------
    drag = {"x": 0, "y": 0, "moved": False}
    def press(e):
        drag["x"], drag["y"], drag["moved"] = e.x, e.y, False
    def move(e):
        drag["moved"] = True
        root.geometry(f"+{root.winfo_x()+e.x-drag['x']}+{root.winfo_y()+e.y-drag['y']}")
    cv.bind("<Button-1>", press)
    cv.bind("<B1-Motion>", move)

    def on_click(e):
        if drag["moved"]:
            return
        item = cv.find_closest(e.x, e.y)[0]
        if item == x_id:
            close()
        elif item == gear_id:
            _open(getattr(ctl, "_vault", "."))
        elif item == help_id:
            set_status("tap mic: start / stop", MUTED)
        elif item in (btn_id, mic_id, ring_id):
            toggle()
    cv.bind("<ButtonRelease-1>", on_click)

    def toggle():
        if state["mode"] == "idle":
            ctl.start()
        elif state["mode"] == "recording":
            set_mic_glyph("⏹")
            state["mode"] = "processing"
            set_status("stopping ...", FG)
            ctl.stop()

    def _open(target):
        try:
            os.startfile(str(target))  # noqa: S606 - intended: open the note/vault for the user
        except Exception:  # noqa: BLE001 - opening is a convenience, never fatal
            pass

    def to_idle(msg, color=MUTED):
        state["mode"] = "idle"
        set_mic_glyph("\U0001F3A4")
        set_mic(MIC_IDLE)
        set_status(msg, color)

    def close():
        if state["mode"] == "recording":
            ctl.abort()  # release the mic; .pcm recovers into a note next launch
        root.destroy()

    # -- pulse the mic while recording + tick the timer --------------------
    def animate():
        if state["mode"] == "recording":
            state["pulse"] = not state["pulse"]
            set_mic(MIC_REC if state["pulse"] else "#cc372f")
            elapsed = int(time.time() - state["t0"])
            set_status(f"● recording  {elapsed // 60:01d}:{elapsed % 60:02d}", MIC_REC)
        root.after(500, animate)

    # -- drain controller events on the UI thread --------------------------
    def pump():
        try:
            while True:
                kind, payload = events.get_nowait()
                if kind == "ready":
                    to_idle("tap to capture")
                elif kind == "recording":
                    state["mode"] = "recording"
                    state["t0"] = time.time()
                elif kind == "status":
                    set_status(payload, FG)
                elif kind == "done":
                    to_idle("saved ✓  opening ...", "#34c759")
                    _open(payload)
                    root.after(2200, lambda: set_status("tap to capture", MUTED))
                elif kind == "error":
                    to_idle(payload[:46], "#ff9f0a")
                elif kind == "fatal":
                    set_status(payload[:46], MIC_REC)
        except queue.Empty:
            pass
        root.after(80, pump)

    root.bind("<Escape>", lambda e: close())
    ctl.warm_load()
    animate()
    pump()
    root.mainloop()
    return 0


def smoke() -> int:
    """Wiring proof: import the pipeline pieces and construct the controller +
    a withdrawn Tk root. No mic, no model load, no GPU. Proves the overlay file
    imports and binds against the real pipeline surface."""
    import tkinter as tk

    from audio import dual_capture  # noqa: F401
    from audio.stt_engine import decode_chunked  # noqa: F401
    from audio.transcript_sink import MarkdownVaultTranscriptSink, vault_path
    from thought_capture.correct import apply_corrections  # noqa: F401
    from thought_capture.library import ingest_capture  # noqa: F401
    from thought_capture.recovery import IncrementalAudioRecorder  # noqa: F401
    from thought_capture.vocab import load_corrections  # noqa: F401

    ctl = CaptureController(queue.Queue())
    assert hasattr(ctl, "start") and hasattr(ctl, "stop") and hasattr(ctl, "abort")
    root = tk.Tk()
    root.withdraw()
    root.destroy()
    print("SMOKE GREEN: overlay imports + pipeline bindings + Tk construct OK.")
    print(f"  vault: {vault_path()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Thought-capture overlay panel.")
    parser.add_argument("--smoke", action="store_true",
                        help="Wiring proof: import + construct, no mic/model.")
    args = parser.parse_args(argv)
    return smoke() if args.smoke else run_ui()


if __name__ == "__main__":
    raise SystemExit(main())
