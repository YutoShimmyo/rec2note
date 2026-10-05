"""MLX Whisper ASR backend for Apple Silicon's Metal GPU."""
from __future__ import annotations

import platform
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .base import ASRBackend, TranscriptionResult


# A pause longer than this normally starts a new thought, speaker, or clip.
# Keeping the prior decoded text past that boundary can seed a repetition loop.
_CONTEXT_RESET_GAP_SECONDS = 5.0
# Preserve long-form context inside a block, but do not allow an unbounded
# recording to carry one mistaken phrase indefinitely.
_MAX_CONTEXT_BLOCK_SECONDS = 300.0


@dataclass(frozen=True)
class _SpeechBlock:
    audio: np.ndarray
    start_seconds: float
    end_seconds: float


class MLXWhisperBackend(ASRBackend):
    """Whisper transcription accelerated by MLX on Apple Silicon."""

    def __init__(self, model_size: str = "mlx-community/whisper-large-v3-turbo"):
        if platform.system() != "Darwin" or platform.machine() != "arm64":
            raise RuntimeError("mlx-whisper requires an Apple Silicon Mac")
        try:
            import mlx_whisper  # noqa: F401 - verify availability for factory fallback
        except ImportError as exc:
            raise RuntimeError("mlx-whisper is not installed; run: uv sync") from exc
        self.model_size = _resolve_model(model_size)

    @property
    def name(self) -> str:
        return f"mlx-whisper/{self.model_size} (Metal GPU)"

    def transcribe(
        self, file_path: str, language: Optional[str] = None
    ) -> TranscriptionResult:
        try:
            import mlx_whisper
        except ImportError as exc:
            raise RuntimeError(
                "mlx-whisper is not installed. Run: uv sync"
            ) from exc

        lang_arg = language if language and language != "auto" else None
        print(f"[ASR] Loading MLX Whisper: {self.model_size} on Metal GPU")
        print(f"[ASR] Transcribing: {file_path}" + (f" (language={lang_arg})" if lang_arg else ""))
        start = time.perf_counter()
        speech_blocks = _load_speech_blocks(file_path)
        if not speech_blocks:
            elapsed = time.perf_counter() - start
            audio_duration = _get_audio_duration(file_path)
            print("[ASR] No speech detected; skipping Whisper decoding.")
            return TranscriptionResult(
                text="",
                language=lang_arg or "unknown",
                language_probability=1.0,
                duration=audio_duration,
                rtf=elapsed / audio_duration if audio_duration > 0 else 0.0,
            )

        print(f"[ASR] VAD: {len(speech_blocks)} speech block(s); context resets at long pauses.")
        texts: list[str] = []
        detected_language = lang_arg or "unknown"
        for index, block in enumerate(speech_blocks, start=1):
            if len(speech_blocks) > 1:
                print(
                    f"[ASR] Block {index}/{len(speech_blocks)}: "
                    f"{block.start_seconds:.1f}s–{block.end_seconds:.1f}s"
                )
            result = mlx_whisper.transcribe(
                block.audio,
                path_or_hf_repo=self.model_size,
                language=lang_arg,
                temperature=0.0,
                # Keep preceding text as a prompt inside one coherent speech
                # block. A new block starts only after a long pause or five
                # minutes, which prevents one bad phrase looping forever.
                condition_on_previous_text=True,
                verbose=False,
            )
            text = (result.get("text") or "").strip()
            if text:
                texts.append(text)
            if lang_arg is None:
                detected_language = result.get("language") or detected_language
                lang_arg = detected_language

        elapsed = time.perf_counter() - start

        text = "\n".join(texts)
        if text:
            print(text)

        audio_duration = _get_audio_duration(file_path)
        rtf = elapsed / audio_duration if audio_duration > 0 else 0.0
        print(f"[ASR] Detected language: {detected_language}")
        print(
            f"[ASR] RTF={rtf:.3f}  "
            f"(elapsed={elapsed:.1f}s / audio={audio_duration:.1f}s)"
        )

        return TranscriptionResult(
            text=text,
            language=detected_language,
            language_probability=1.0,
            duration=audio_duration,
            rtf=rtf,
        )


def _resolve_model(model: str) -> str:
    """Map familiar Whisper aliases to the corresponding MLX Community model."""
    if "/" in model or model.startswith("."):
        return model
    return f"mlx-community/whisper-{model}"


def _load_speech_blocks(file_path: str) -> list[_SpeechBlock]:
    """Return VAD-delimited audio blocks suitable for contextual decoding.

    MLX Whisper processes every supplied sample.  We retain nearby pauses and
    context inside each block, but exclude long silent gaps from decoding and
    reset the text prompt across a new section of the recording.
    """
    from faster_whisper.audio import decode_audio
    from faster_whisper.vad import get_speech_timestamps

    audio = decode_audio(file_path, sampling_rate=16_000)
    speech_segments = get_speech_timestamps(audio, sampling_rate=16_000)
    if not speech_segments:
        return []

    ranges: list[tuple[int, int]] = []
    block_start = speech_segments[0]["start"]
    block_end = speech_segments[0]["end"]
    max_block_samples = int(_MAX_CONTEXT_BLOCK_SECONDS * 16_000)
    max_gap_samples = int(_CONTEXT_RESET_GAP_SECONDS * 16_000)

    for segment in speech_segments[1:]:
        starts_new_block = (
            segment["start"] - block_end > max_gap_samples
            or segment["end"] - block_start > max_block_samples
        )
        if starts_new_block:
            ranges.append((block_start, block_end))
            block_start, block_end = segment["start"], segment["end"]
        else:
            block_end = segment["end"]
    ranges.append((block_start, block_end))

    blocks: list[_SpeechBlock] = []
    for start, end in ranges:
        # A single continuous speech segment can exceed the block cap.
        while end - start > max_block_samples:
            split_end = start + max_block_samples
            blocks.append(_SpeechBlock(audio[start:split_end], start / 16_000, split_end / 16_000))
            start = split_end
        blocks.append(_SpeechBlock(audio[start:end], start / 16_000, end / 16_000))
    return blocks


def _get_audio_duration(file_path: str) -> float:
    """Return audio duration in seconds via ffprobe, if available."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0
