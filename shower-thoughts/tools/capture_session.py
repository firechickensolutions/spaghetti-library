"""Personal thought-capture session.

Speak your thinking, get a durable, coherent Markdown note in your vault.
Mic-only
(operator_mic). STT is Parakeet-TDT via onnx-asr (ParakeetEngine).

No chop: the whole session's audio is accumulated, then
transcribed in ONE coherent Parakeet pass at stop. Unlike a real-time transcriber, thinking-capture has no real-time
constraint, so it does not slice the monologue into utterances — slicing only
shreds context and fragments the transcript. One pass = one coherent note.

Usage:
    python tools/capture_session.py                 # live mic capture until Ctrl-C
    python tools/capture_session.py --seconds 300   # live capture, auto-stop after N s
    python tools/capture_session.py --self-test     # wiring proof: scripted engine, no mic/GPU

Env overrides (Rule 8):
  SHOWER_CAPTURE_VAULT_PATH    vault dir (default ~/ShowerThoughts)
  SHOWER_PARAKEET_MODEL / SHOWER_PARAKEET_PROVIDERS   STT engine
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from audio.transcript_sink import MarkdownVaultTranscriptSink, vault_path  # noqa: E402


def _is_mic_packet(source_stream: str) -> bool:
    """Mic-only invariant: only operator_mic packets are captured; any
    other stream (system_loopback) is dropped so a personal-mode note never
    persists non-mic audio. Pure predicate -- unit-testable on any Python."""
    return source_stream == "operator_mic"


def transcribe_session(stt: object, pcm: bytes) -> str:
    """Transcribe a whole session's audio (D27), chunked for length.

    No VAD chop (context stays whole), but the audio is split into safe windows
    because Parakeet has a sequence-length ceiling — a single decode of a long
    capture crashes onnxruntime (observed at ~14 min). decode_chunked windows it
    (default 180s), decodes each, and joins; a short session is still one pass."""
    if not pcm:
        return ""
    from audio.stt_engine import decode_chunked  # noqa: PLC0415

    return decode_chunked(stt, pcm, 16000)


def _run_live(stt: object, sink: MarkdownVaultTranscriptSink, session_id: str,
              seconds: float | None) -> int:
    """Capture the operator microphone (mic-only) into an in-memory buffer until
    Ctrl-C or `seconds`, then transcribe the WHOLE session in one coherent pass
    and write the note. No per-utterance decode during capture, so the capture
    thread never blocks (D26) and nothing is dropped; no chop (D27)."""
    # Imported here, not at module load: dual_capture pulls in audioop (used only
    # for live capture), removed from the stdlib in Python 3.13+. The self-test
    # and the wiring tests never reach this path, so they stay import-clean.
    try:
        from audio import dual_capture
    except ModuleNotFoundError as exc:
        print(f"HALT: live capture is unavailable in this environment: {exc}")
        print("  audio/dual_capture needs the 'audioop' module, removed from the")
        print("  Python stdlib in 3.13+. Install the backport to enable live capture:")
        print("      pip install audioop-lts")
        print("  (The --self-test wiring proof does not need it.)")
        return 3

    if not dual_capture.loopback_available():
        print("note: WASAPI loopback unavailable (expected for mic-only capture).")
        print(f"      reason: {dual_capture.import_error()}")

    # Crash recovery: append mic PCM to a .pcm file on disk as it
    # arrives, and transcribe FROM the file at stop. A crash/kill mid-capture
    # leaves the .pcm for the next run to recover; capture-time memory is bounded.
    from thought_capture.recovery import IncrementalAudioRecorder  # noqa: PLC0415

    recorder = IncrementalAudioRecorder(session_id)
    captured = {"packets": 0, "warned": False}
    warn_packets = int(float(os.environ.get("SHOWER_CAPTURE_WARN_SECONDS", "1800")) * 10)

    def on_packet(p: dual_capture.CapturePacket) -> None:
        # Capture thread: only append the mic PCM (microseconds), flushed to disk.
        # No decode here, so the OS audio buffer never overflows.
        if _is_mic_packet(p.source_stream):
            recorder.write(p.pcm)
            captured["packets"] += 1
            if not captured["warned"] and captured["packets"] >= warn_packets:
                captured["warned"] = True
                mins = warn_packets // 600
                print(f"\nnote: capture has passed ~{mins} min. It is saved to disk as you")
                print("      speak (safe), but a faster decode comes from Ctrl-C now and")
                print("      segmenting. Continuing is fine.")

    cap = dual_capture.DualStreamCapturer(
        on_packet=on_packet, clock_ms=lambda: int(time.time() * 1000)
    )
    # mic_only: start only the operator_mic stream. Starting loopback
    # too would capture system audio we discard and run two concurrent PyAudio
    # instances, which segfault PortAudio here.
    started = cap.start(mic_only=True)
    if "operator_mic" not in started:
        print("HALT: microphone capture did not start. Confirm a default input device")
        print("  is present and pyaudiowpatch is installed (pip install -e .[capture]).")
        return 2

    print(f"capturing (session {session_id}) - speak now. Ctrl-C to stop.")
    try:
        if seconds is not None:
            time.sleep(seconds)
        else:
            while True:
                time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nstopping...")
    finally:
        cap.stop()  # joins the capture thread -> the .pcm holds the full session

    secs = captured["packets"] // 10
    print(f"captured {captured['packets']} mic packets (~{secs}s of audio).")
    if captured["packets"] == 0:
        recorder.discard()  # nothing captured -> drop the empty .pcm
        print("note: no audio reached the capture. Is the default input device the mic")
        print("      you spoke into? Check Windows Sound settings, then re-run.")
        return 0
    print(f"transcribing the full session in one coherent pass (~{secs}s of audio)...")
    text = transcribe_session(stt, recorder.read_all())
    if not text:
        # Real audio, empty decode -> PRESERVE it (never silently delete a capture
        # that might be salvageable with a better decode / louder re-listen).
        failed = recorder.preserve_failed()
        print("note: audio captured but transcribed empty -- likely spoken too quietly")
        print(f"      or low mic gain. Audio preserved for salvage at: {failed}")
        return 0
    # Safe verbatim correction: exact known mis-hears -> canonical. Corruption-free by construction (whole-token exact match on
    # non-word keys). Meaning-level fixes come from priming the extraction LLM.
    from thought_capture.correct import apply_corrections  # noqa: PLC0415
    from thought_capture.vocab import load_corrections  # noqa: PLC0415

    text, fixes = apply_corrections(text, load_corrections())
    if fixes:
        shown = ", ".join(f"{o}->{r}" for o, r in fixes[:6])
        print(f"corrected {len(fixes)} known mis-hear(s): {shown}")
    path = sink.write_session_note(session_id, text)
    # The note (transcript) is the floor and is now on disk -> discard the .pcm
    # BEFORE the multi-second enrich, so a crash during enrich cannot leave both
    # a note and an orphan (which would recover into a DUPLICATE note next run).
    recorder.discard()
    print(f"note: {path}")
    # D28/D29: enrich the durable transcript note with the semantic
    # taxonomy and add it to the retrievable library. Lazy import keeps the
    # self-test and unit tests import-clean. ingest_capture degrades gracefully:
    # the transcript note above is the floor and is never put at risk here. A
    # crash here leaves the note un-enriched (re-ingestable), never lost.
    from thought_capture.library import ingest_capture  # noqa: PLC0415

    ingest_capture(path, text)
    return 0


def run_scripted_capture(vault_dir: Path, transcript: str) -> Path:
    """Wiring proof (no mic, no GPU): a scripted engine 'transcribes' the session
    to `transcript`, written as a coherent prose note. The deterministic proxy
    for the live capture -> whole-session decode -> note path, pinned in
    tests/test_capture_session.py."""
    from audio.stt_engine import SttResult

    class _ScriptedEngine:
        def decode(self, pcm: bytes, sample_rate_hz: int) -> SttResult:
            return SttResult(partials=[], final=transcript)

    sink = MarkdownVaultTranscriptSink(vault_dir=vault_dir)
    stt = _ScriptedEngine()
    session_id = f"selftest-{uuid.uuid4()}"
    text = transcribe_session(stt, b"\x00\x01" * 1600)
    return sink.write_session_note(session_id, text)


def _run_self_test(vault_dir: Path) -> int:
    transcript = (
        "I think the actual constraint is the handoff between trades. "
        "The reusable shape is a single durable note per session. "
        "Next move is to walk a real five minute capture and read the note back."
    )
    note_path = run_scripted_capture(vault_dir, transcript)
    if not note_path.is_file():
        print("SELF-TEST FAILED: no note was written.")
        return 1
    print("SELF-TEST GREEN: capture -> whole-session decode -> coherent note proven.")
    print(f"  note: {note_path}")
    print("  ---")
    print(note_path.read_text(encoding="utf-8"))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Personal thought-capture session."
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=None,
        help="Auto-stop after N seconds (default: run until Ctrl-C).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Wiring proof with a scripted engine - no mic, no GPU. Throwaway note.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        tmp = Path(tempfile.mkdtemp(prefix="shower-capture-selftest-"))
        return _run_self_test(tmp)

    sink = MarkdownVaultTranscriptSink(vault_path())
    print(f"vault: {vault_path()}")
    from audio.stt_engine import ParakeetEngine

    stt = ParakeetEngine()
    # Warm-load the model before capture so the stop-time decode is just the
    # decode, not load + decode.
    print("loading speech model (Parakeet, one-time)...")
    stt.decode(b"\x00\x00" * 1600, 16000)
    print("model ready.")

    # Crash recovery: turn any .pcm left by an interrupted prior capture into a
    # note before starting a new session.
    from thought_capture.recovery import orphans, recover  # noqa: PLC0415

    for orphan in orphans():
        print(f"recovering interrupted capture {orphan.stem} ...")
        try:
            note = recover(orphan, stt, sink)
            print(f"  recovered -> {note}" if note else "  (empty capture discarded)")
        except Exception as exc:  # noqa: BLE001 - keep the .pcm for a later retry
            print(f"  recovery failed ({exc}); left on disk to retry next run.")

    session_id = str(uuid.uuid4())
    return _run_live(stt, sink, session_id, args.seconds)


if __name__ == "__main__":
    raise SystemExit(main())
