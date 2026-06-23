"""Backend-native Windows dual-stream capture — Decision L18.

Captures two role-labeled audio streams on the operator's Windows machine:
  - operator_mic     : the operator's microphone (default input device)
  - system_loopback  : the remote buyer's voice, via WASAPI render-endpoint
                       loopback on the default output device

Both are normalized to 16 kHz mono signed-16-bit PCM and emitted as 100 ms
packets tagged with `source_stream`, matching the AudioPacket contract
(api/routes/audio.py) and the pipeline's per-(session, source_stream) keying.

Why backend-native: the browser cannot access WASAPI loopback, so the remote
buyer's voice on a headphoned video call is unreachable from getUserMedia.
PyAudioWPatch exposes the render-endpoint loopback device directly.

Degradation: PyAudioWPatch is a Windows-only optional dependency
(`pip install -e .[capture]`). When it is unavailable (non-Windows dev/CI, or
not installed), `loopback_available()` returns False and the caller falls back
to single-stream operator_mic capture — the system never hard-fails on import.

Process-specific (per-app) loopback is explicitly out of scope for v1; this module uses system render-endpoint
loopback plus device preflight, per the dual-stream research recommendation.
"""

from __future__ import annotations

import audioop
import threading
from dataclasses import dataclass
from typing import Callable, Literal

SourceStream = Literal["operator_mic", "system_loopback"]

TARGET_SAMPLE_RATE_HZ = 16000
TARGET_CHANNELS = 1
TARGET_SAMPLE_WIDTH = 2  # LINEAR16
PACKET_DURATION_MS = 100
TARGET_FRAMES_PER_PACKET = TARGET_SAMPLE_RATE_HZ * PACKET_DURATION_MS // 1000

# PyAudioWPatch is Windows-only and optional. Probe at import; never raise.
try:  # pragma: no cover - import availability is environment-dependent
    import pyaudiowpatch as _pyaudio  # type: ignore

    _IMPORT_ERROR: str | None = None
except Exception as exc:  # noqa: BLE001 - any import failure degrades to single-stream
    _pyaudio = None  # type: ignore
    _IMPORT_ERROR = str(exc)


def loopback_available() -> bool:
    """True when WASAPI loopback capture can be attempted on this machine."""
    return _pyaudio is not None


def import_error() -> str | None:
    """The import failure reason, for preflight/diagnostic surfacing."""
    return _IMPORT_ERROR


@dataclass(frozen=True)
class DeviceInfo:
    index: int
    name: str
    kind: Literal["input", "loopback"]
    default_sample_rate: int
    channels: int


@dataclass(frozen=True)
class CapturePacket:
    """One normalized 100 ms packet ready to hand to the pipeline."""

    source_stream: SourceStream
    pcm: bytes  # 16 kHz mono LINEAR16, TARGET_FRAMES_PER_PACKET frames
    captured_at_ms: int


def enumerate_devices() -> list[DeviceInfo]:
    """List the default input device and the default WASAPI loopback endpoint.

    Returns an empty list when loopback is unavailable. Preflight reads this to
    confirm the operator's mic and the call-output endpoint are both present.
    """
    if _pyaudio is None:
        return []
    pa = _pyaudio.PyAudio()
    try:
        devices: list[DeviceInfo] = []
        default_in = pa.get_default_input_device_info()
        devices.append(
            DeviceInfo(
                index=int(default_in["index"]),
                name=str(default_in["name"]),
                kind="input",
                default_sample_rate=int(default_in["defaultSampleRate"]),
                channels=int(default_in["maxInputChannels"]),
            )
        )
        # get_default_wasapi_loopback resolves the render endpoint that mirrors
        # the default output device (where the call audio is played).
        loopback = pa.get_default_wasapi_loopback()
        devices.append(
            DeviceInfo(
                index=int(loopback["index"]),
                name=str(loopback["name"]),
                kind="loopback",
                default_sample_rate=int(loopback["defaultSampleRate"]),
                channels=int(loopback["maxInputChannels"]),
            )
        )
        return devices
    finally:
        pa.terminate()


def _normalize_to_target(
    pcm: bytes,
    src_rate: int,
    src_channels: int,
    rate_state,
) -> tuple[bytes, object]:
    """Downmix to mono and resample to 16 kHz, carrying ratecv state across calls."""
    if src_channels > 1:
        pcm = audioop.tomono(pcm, TARGET_SAMPLE_WIDTH, 0.5, 0.5)
    if src_rate != TARGET_SAMPLE_RATE_HZ:
        pcm, rate_state = audioop.ratecv(
            pcm, TARGET_SAMPLE_WIDTH, TARGET_CHANNELS, src_rate, TARGET_SAMPLE_RATE_HZ, rate_state
        )
    return pcm, rate_state


class _StreamCapture(threading.Thread):
    """Captures one source, normalizes, and packetizes into 100 ms chunks."""

    def __init__(
        self,
        *,
        source_stream: SourceStream,
        device_index: int,
        src_rate: int,
        src_channels: int,
        on_packet: Callable[[CapturePacket], None],
        clock_ms: Callable[[], int],
    ) -> None:
        super().__init__(name=f"capture-{source_stream}", daemon=True)
        self._source_stream = source_stream
        self._device_index = device_index
        self._src_rate = src_rate
        self._src_channels = src_channels
        self._on_packet = on_packet
        self._clock_ms = clock_ms
        self._stop = threading.Event()
        self._target_packet_bytes = TARGET_FRAMES_PER_PACKET * TARGET_SAMPLE_WIDTH

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:  # pragma: no cover - requires live audio hardware
        if _pyaudio is None:
            return
        pa = _pyaudio.PyAudio()
        rate_state = None
        residual = b""
        # Read ~100 ms of source frames per loop; normalization changes the
        # frame count, so we re-packetize against a residual buffer.
        frames_per_read = max(1, self._src_rate * PACKET_DURATION_MS // 1000)
        stream = pa.open(
            format=_pyaudio.paInt16,
            channels=self._src_channels,
            rate=self._src_rate,
            input=True,
            input_device_index=self._device_index,
            frames_per_buffer=frames_per_read,
        )
        try:
            while not self._stop.is_set():
                raw = stream.read(frames_per_read, exception_on_overflow=False)
                norm, rate_state = _normalize_to_target(
                    raw, self._src_rate, self._src_channels, rate_state
                )
                residual += norm
                while len(residual) >= self._target_packet_bytes:
                    chunk = residual[: self._target_packet_bytes]
                    residual = residual[self._target_packet_bytes :]
                    self._on_packet(
                        CapturePacket(
                            source_stream=self._source_stream,
                            pcm=chunk,
                            captured_at_ms=self._clock_ms(),
                        )
                    )
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()


class DualStreamCapturer:
    """Owns the operator_mic + system_loopback capture threads for one session.

    on_packet is invoked from the capture threads with normalized CapturePackets;
    the caller routes them into the pipeline per (session_id, source_stream).
    """

    def __init__(
        self,
        *,
        on_packet: Callable[[CapturePacket], None],
        clock_ms: Callable[[], int],
    ) -> None:
        self._on_packet = on_packet
        self._clock_ms = clock_ms
        self._threads: list[_StreamCapture] = []

    def start(self, mic_only: bool = False) -> list[SourceStream]:
        """Start the capture streams. Returns the streams actually started.

        mic_only=True starts ONLY operator_mic (one PyAudio instance, one
        stream) for the personal thought-capture mode. It also
        sidesteps the dual-stream concurrency crash where two concurrent
        PyAudio instances segfault PortAudio on some stacks (Python 3.14 +
        PyAudioWPatch on this machine — see capture-segfault ticket).

        With mic_only False (default, the L18 discovery path) both streams
        start when available. If loopback is unavailable, starts operator_mic
        only and returns ["operator_mic"] so the caller can surface the
        single-stream degrade.
        """
        if _pyaudio is None:
            return []
        devices = {d.kind: d for d in enumerate_devices()}
        started: list[SourceStream] = []
        if "input" in devices:
            mic = devices["input"]
            t = _StreamCapture(
                source_stream="operator_mic",
                device_index=mic.index,
                src_rate=mic.default_sample_rate,
                src_channels=min(mic.channels, 2) or 1,
                on_packet=self._on_packet,
                clock_ms=self._clock_ms,
            )
            self._threads.append(t)
            t.start()
            started.append("operator_mic")
        if not mic_only and "loopback" in devices:
            lb = devices["loopback"]
            t = _StreamCapture(
                source_stream="system_loopback",
                device_index=lb.index,
                src_rate=lb.default_sample_rate,
                src_channels=min(lb.channels, 2) or 1,
                on_packet=self._on_packet,
                clock_ms=self._clock_ms,
            )
            self._threads.append(t)
            t.start()
            started.append("system_loopback")
        return started

    def stop(self) -> None:
        for t in self._threads:
            t.stop()
        for t in self._threads:
            t.join(timeout=2.0)
        self._threads.clear()
