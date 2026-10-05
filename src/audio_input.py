"""Prepare recording formats that need conversion before ASR."""
from contextlib import contextmanager
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Iterator


@contextmanager
def prepare_audio_input(file_path: str) -> Iterator[str]:
    """Convert VOB's first audio stream to temporary mono 16 kHz PCM."""
    if Path(file_path).suffix.lower() != ".vob":
        yield file_path
        return

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("VOB 入力には ffmpeg が必要です。macOS: brew install ffmpeg")

    with tempfile.TemporaryDirectory(prefix="rec2note-vob-") as directory:
        wav_path = str(Path(directory) / "audio.wav")
        print(f"[Audio] VOB の音声を抽出: {file_path}")
        result = subprocess.run(
            [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error",
             "-i", str(Path(file_path).resolve()), "-map", "0:a:0", "-vn",
             "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav_path],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"VOB の音声抽出に失敗しました: {file_path}\n{result.stderr.strip()}"
            )
        yield wav_path
