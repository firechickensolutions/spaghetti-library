"""Speech-to-text engine: NVIDIA Parakeet-TDT via onnx-asr (ONNX Runtime).

Interface-first (the SttEngine Protocol) so callers can inject a scripted engine
in tests without a model download or a GPU. Parakeet runs fully local on CPU
(~13x real-time) or on the GPU when the CUDA DLLs resolve.

Env overrides:
  SHOWER_PARAKEET_MODEL              default nemo-parakeet-tdt-0.6b-v3
  SHOWER_PARAKEET_PROVIDERS         default CPUExecutionProvider
  SHOWER_PARAKEET_MAX_DECODE_SECONDS default 180
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class SttResult:
    """One decoded utterance. `partials` is the segment stream (empty for the
    single-shot Parakeet transducer); `final` is the durable concatenated text."""

    partials: list[str] = field(default_factory=list)
    final: str = ""
    language: str | None = None


class SttEngine(Protocol):
    """Decode interface the capture path depends on."""

    def decode(self, pcm: bytes, sample_rate_hz: int) -> SttResult: ...


def _add_cuda_dll_dirs() -> None:
    """Windows GPU path: put the CUDA runtime DLLs on the search path so the
    onnxruntime CUDA provider can load cuBLAS/cuDNN.

    The nvidia-*-cu12 pip packages ship the DLLs under site-packages/nvidia/*/bin,
    but they are loaded by plain name, so they must be on PATH. No-op off Windows
    and when the packages are absent (the CPU path needs none of this); idempotent.
    """
    if sys.platform != "win32":
        return
    import glob  # noqa: PLC0415
    import importlib.util  # noqa: PLC0415

    dirs: list[str] = []
    for pkg in ("nvidia.cublas", "nvidia.cudnn", "nvidia.cuda_runtime", "nvidia.cuda_nvrtc"):
        spec = importlib.util.find_spec(pkg)
        if spec is None or not spec.submodule_search_locations:
            continue
        loc = spec.submodule_search_locations[0]
        for dll in glob.glob(os.path.join(loc, "**", "*.dll"), recursive=True):
            d = os.path.dirname(dll)
            if d not in dirs:
                dirs.append(d)
    if not dirs:
        return
    current_path = os.environ.get("PATH", "")
    missing = [d for d in dirs if d not in current_path]
    if missing:
        os.environ["PATH"] = os.pathsep.join(missing) + os.pathsep + current_path
    for d in dirs:
        try:
            os.add_dll_directory(d)
        except OSError:
            pass


def decode_chunked(
    engine: SttEngine, pcm: bytes, sample_rate_hz: int, max_seconds: float | None = None
) -> str:
    """Decode arbitrarily long PCM by splitting into <= max_seconds windows.

    Parakeet has a sequence-length ceiling: a single decode of a long capture
    raises (a ~14 min session crashed onnxruntime with a broadcast-axis error in
    the encoder). Split the audio into safe windows, decode each, and join with
    paragraph breaks. Boundaries are clean (no overlap) — at most a fractional
    word is lost per join, negligible for a multi-minute window.

    Env: SHOWER_PARAKEET_MAX_DECODE_SECONDS (default 180, safely under the ceiling)."""
    if not pcm:
        return ""
    if max_seconds is None:
        max_seconds = float(os.environ.get("SHOWER_PARAKEET_MAX_DECODE_SECONDS", "180"))
    chunk_bytes = int(max_seconds * sample_rate_hz * 2)  # LINEAR16 = 2 bytes/sample
    if chunk_bytes <= 0 or len(pcm) <= chunk_bytes:
        return engine.decode(pcm, sample_rate_hz).final.strip()
    parts: list[str] = []
    for start in range(0, len(pcm), chunk_bytes):
        seg = pcm[start : start + chunk_bytes]
        if len(seg) % 2:  # keep whole 2-byte samples
            seg = seg[:-1]
        if not seg:
            continue
        text = engine.decode(seg, sample_rate_hz).final.strip()
        if text:
            parts.append(text)
    return "\n\n".join(parts)


class ParakeetEngine:
    """NVIDIA Parakeet-TDT speech-to-text via onnx-asr (ONNX Runtime).

    A transducer: fast, stays silent on non-speech (no Whisper-style hallucinated
    text), and emits punctuation and casing. Runs local on CPU (~13x real-time) or
    GPU (CUDAExecutionProvider when the CUDA DLLs resolve). No NeMo dependency.

    CPU is the default provider: plenty for offline capture, and it avoids
    onnxruntime's noisy CUDA-provider DLL probing when the GPU is not needed. Set
    SHOWER_PARAKEET_PROVIDERS to CUDAExecutionProvider,CPUExecutionProvider to opt
    into the GPU.

    Env overrides:
      SHOWER_PARAKEET_MODEL      default nemo-parakeet-tdt-0.6b-v3
      SHOWER_PARAKEET_PROVIDERS  default CPUExecutionProvider
    """

    def __init__(
        self, model: str | None = None, providers: list[str] | None = None
    ) -> None:
        self.model_name = model or os.environ.get(
            "SHOWER_PARAKEET_MODEL", "nemo-parakeet-tdt-0.6b-v3"
        )
        self.providers = providers or os.environ.get(
            "SHOWER_PARAKEET_PROVIDERS", "CPUExecutionProvider"
        ).split(",")
        self._model: object | None = None

    def _ensure_loaded(self) -> object:
        if self._model is not None:
            return self._model
        # Add the CUDA DLL dirs so the onnxruntime CUDA provider can load if the
        # user opted into the GPU via SHOWER_PARAKEET_PROVIDERS. No-op for CPU.
        if any("CUDA" in p for p in self.providers):
            _add_cuda_dll_dirs()
        import onnx_asr  # noqa: PLC0415

        self._model = onnx_asr.load_model(self.model_name, providers=self.providers)
        return self._model

    def decode(self, pcm: bytes, sample_rate_hz: int) -> SttResult:
        if not pcm:
            return SttResult()
        import numpy as np  # noqa: PLC0415

        model = self._ensure_loaded()
        audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        text = (model.recognize(audio) or "").strip()
        # Parakeet is single-shot (no streaming partials); emit one final.
        return SttResult(partials=[], final=text)
