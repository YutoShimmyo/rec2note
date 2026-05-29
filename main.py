"""Recording → desired artifact — main entry point.

A *skill* selects what to produce (meeting minutes, a magic lecture note, …)
and in which formats (md, pdf). See skills/README.md.

Usage:
    uv run main.py input/meeting.mp4
    uv run main.py input/meeting.mp4 --minutes-backend api
    uv run main.py input/talk.mp4 --skill magic-lecture --output md,pdf
    uv run main.py input/meeting.mp4 --config my_config.yaml
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from src.config import load_config, apply_cli_overrides, apply_skill_defaults
from src.asr import create_backend
from src.summarizer import create_summarizer
from src.skills import load_skill, list_skills, resolve_prompt_language
from src.prompts import load_prompt
from src.exporters import create_exporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="minutes",
        description="Transcribe audio/video recordings and turn them into the artifact a skill defines.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Transcription only (fastest)
  uv run main.py input/meeting.mp4

  # Meeting minutes via API (default skill)
  uv run main.py input/meeting.mp4 --minutes-backend api

  # Magic lecture note + PDF
  uv run main.py input/talk.mp4 --skill magic-lecture --output md,pdf

  # Force a specific ASR model
  uv run main.py input/meeting.mp4 --asr-model large-v3

  # Use a custom config file
  uv run main.py input/meeting.mp4 --config my_config.yaml
""",
    )

    parser.add_argument(
        "audio_file",
        nargs="?",
        default=None,
        help="Path to the audio/video file (m4a, mp3, mp4, wav, …)",
    )

    parser.add_argument(
        "--config",
        metavar="PATH",
        help="Path to config.yaml (default: config.yaml in project root)",
    )

    parser.add_argument(
        "--skill",
        metavar="NAME",
        help="Skill (recipe) to run, e.g. 'meeting-minutes' or 'magic-lecture' (default: meeting-minutes)",
    )
    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="List available skills and exit",
    )

    # General
    parser.add_argument(
        "--language",
        choices=["ja", "en", "auto"],
        help="Audio language. 'auto' lets Whisper detect it (default: auto)",
    )
    parser.add_argument(
        "--profile",
        choices=["fast", "standard", "quality"],
        help="Quality profile; affects ASR preset auto-selection (default: standard)",
    )

    # ASR
    asr = parser.add_argument_group("ASR options")
    asr.add_argument(
        "--asr-preset",
        choices=["A", "B", "C", "D"],
        metavar="PRESET",
        help=(
            "ASR preset: "
            "A=English·HQ, B=English·Standard, "
            "C=Multilingual·HQ, D=Multilingual·Standard"
        ),
    )
    asr.add_argument(
        "--asr-backend",
        choices=["faster_whisper", "parakeet"],
        help="Override ASR backend regardless of preset",
    )
    asr.add_argument(
        "--asr-model",
        metavar="MODEL",
        help="Override ASR model (e.g. 'large-v3', 'medium', 'small')",
    )

    # Generation / output
    mins = parser.add_argument_group("Generation & output options")
    mins.add_argument(
        "--minutes-backend",
        choices=["none", "api", "local"],
        help="Generation backend (default from skill; 'none' = transcription only)",
    )
    mins.add_argument(
        "--output",
        metavar="FORMATS",
        help="Comma-separated output formats, e.g. 'md,pdf' (default from skill)",
    )
    mins.add_argument(
        "--minutes-language",
        choices=["ja", "en", "auto"],
        help=(
            "Override the prompt/output language. "
            "'auto' follows the skill (audio language or the skill's fixed language)."
        ),
    )
    mins.add_argument(
        "--minutes-local-runtime",
        choices=["mlx-lm", "mlx-vlm", "ollama"],
        help=(
            "Local LLM runtime when --minutes-backend=local (default: mlx-vlm). "
            "Use mlx-vlm for multimodal models like Gemma 4 E4B."
        ),
    )
    mins.add_argument(
        "--minutes-provider",
        choices=["openai", "gemini"],
        help="API provider when --minutes-backend=api (default from skill/config; openai recommended)",
    )
    mins.add_argument(
        "--minutes-model",
        metavar="MODEL",
        help="Model path/name for generation (HuggingFace ID, local path, or API model)",
    )
    mins.add_argument(
        "--minutes-max-tokens",
        type=int,
        metavar="N",
        help="Max output tokens for generation (default from skill)",
    )

    # Legacy flags kept for backward compatibility
    legacy = parser.add_argument_group("Legacy options (backward compatibility)")
    legacy.add_argument(
        "--summarize",
        action="store_true",
        help="[Legacy] Enable local summarization (same as --minutes-backend local)",
    )
    legacy.add_argument(
        "--use-gemini",
        action="store_true",
        help="[Legacy] Enable API summarization (same as --minutes-backend api)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if getattr(args, "list_skills", False):
        print("Available skills:")
        for s in list_skills():
            print(f"  - {s}")
        return

    if not args.audio_file:
        parser.error("audio_file is required (or use --list-skills)")

    # ── Load config + resolve skill ───────────────────────────────────────────
    cfg = load_config(args.config)

    # Skill selection: CLI > config.yaml. Its defaults layer under CLI overrides.
    skill_name = getattr(args, "skill", None) or cfg.skill.name
    try:
        skill = load_skill(skill_name)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    cfg = apply_skill_defaults(cfg, skill.defaults, skill.outputs)
    cfg = apply_cli_overrides(cfg, args)

    # Handle legacy flags
    if getattr(args, "use_gemini", False) and cfg.minutes.backend == "none":
        cfg.minutes.backend = "api"
    if getattr(args, "summarize", False) and cfg.minutes.backend == "none":
        cfg.minutes.backend = "local"

    # ── Validate input file ───────────────────────────────────────────────────
    audio_path = args.audio_file
    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    base_name = Path(audio_path).stem
    transcript_dir = Path("output/transcripts")
    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcript_file = transcript_dir / f"{base_name}.txt"

    out_dir = Path("output") / skill.subdir
    out_stem = f"{base_name}{skill.output_stem_suffix}"

    total_start = time.perf_counter()
    print(f"[Skill] {skill.name} — {skill.description}")

    # ── Step 1: Transcription ─────────────────────────────────────────────────
    _section("Step 1: Transcription")

    detected_lang: str | None = None
    if transcript_file.exists():
        print(f"Transcript already exists at {transcript_file} — skipping.")
        transcript = transcript_file.read_text(encoding="utf-8")
    else:
        asr = create_backend(
            preset=cfg.asr.preset,
            backend_override=cfg.asr.backend,
            model_override=cfg.asr.model,
            device=cfg.asr.device,
            profile=cfg.profile,
            language=cfg.language,
        )
        print(f"[ASR] Backend: {asr.name}")
        result = asr.transcribe(
            audio_path,
            language=cfg.language if cfg.language != "auto" else None,
        )
        transcript = result.text
        detected_lang = result.language
        transcript_file.write_text(transcript, encoding="utf-8")
        print(f"\n[ASR] Transcript saved: {transcript_file}")

    # ── Step 2: Generation ────────────────────────────────────────────────────
    _section(f"Step 2: Generation ({skill.name})")

    written: list[Path] = []
    if cfg.minutes.backend == "none":
        print(
            "Skipped (backend = none). Enable generation with:\n"
            "  --minutes-backend api    (requires an API key in .env)\n"
            "  --minutes-backend local  (requires mlx or Ollama)"
        )
    else:
        summarizer = create_summarizer(
            backend=cfg.minutes.backend,
            api_provider=cfg.minutes.api.provider,
            api_model=cfg.minutes.api.model,
            local_runtime=cfg.minutes.local.runtime,
            model_path=cfg.minutes.local.model_path,
            ollama_model=cfg.minutes.local.ollama_model,
            ollama_url=cfg.minutes.local.ollama_url,
        )
        if summarizer:
            print(f"[Generate] Backend: {summarizer.name}")

            # Prompt language: skill decides; --minutes-language can force it.
            prompt_lang = resolve_prompt_language(skill, cfg.language, detected_lang)
            out_lang = cfg.minutes.output_language
            if out_lang in ("ja", "en"):
                prompt_lang = out_lang
            print(f"[Generate] Prompt language: {prompt_lang}")

            system_prompt = load_prompt(
                prompt_lang,
                prompt_dir=skill.prompt_dir,
                default_language=skill.default_language,
            )
            content = summarizer.summarize(
                transcript,
                language=prompt_lang,
                system_prompt=system_prompt,
                max_tokens=cfg.minutes.max_tokens,
            )

            # ── Step 3: Export ────────────────────────────────────────────────
            out_dir.mkdir(parents=True, exist_ok=True)
            for fmt in cfg.skill.outputs:
                exporter = create_exporter(fmt)
                path = out_dir / f"{out_stem}.{exporter.extension}"
                res = exporter.export(content, out_path=path, title=base_name)
                written.append(res.path)
                print(f"[Export] {fmt}: {res.path}")

    # ── Summary ───────────────────────────────────────────────────────────────
    total_elapsed = time.perf_counter() - total_start
    _section(f"Done!  Total time: {total_elapsed:.1f}s")
    print(f"  Transcript : {transcript_file}")
    for p in written:
        print(f"  Output     : {p}")


def _section(title: str) -> None:
    bar = "=" * 50
    print(f"\n{bar}\n{title}\n{bar}")


if __name__ == "__main__":
    main()
