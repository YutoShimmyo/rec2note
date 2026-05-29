# Skills

A **skill** is a declarative recipe for turning a recording into a specific
kind of artifact — meeting minutes, a detailed lecture note, a cleaned-up
transcript, etc. Skills are the heart of this platform: you (and anyone else)
can add new use-cases **without writing any Python**.

Pick a skill on the command line:

```bash
uv run main.py input/talk.mp4 --skill magic-lecture
```

If `--skill` is omitted, `meeting-minutes` is used (backward compatible).

## Anatomy of a skill

```text
skills/<name>/
├── skill.yaml          # metadata, generation defaults, outputs
└── prompts/
    ├── ja.md           # system prompt (Japanese)
    └── en.md           # system prompt (English, optional)
```

## `skill.yaml` fields

```yaml
name: magic-lecture                 # skill id (matches the folder name)
description: "..."                  # one-line description

prompt:
  dir: prompts                      # folder (relative to skill.yaml) holding <lang>.md
  language: fixed                   # "audio" = follow the recording, "fixed" = always one language
  fixed_language: ja                # used when language: fixed
  default_language: ja              # fallback when a <lang>.md is missing

defaults:                           # generation defaults — override config.yaml, overridden by CLI
  backend: api                      # none | api | local
  api: { provider: openai, model: gpt-5.5 }
  local: { runtime: mlx-vlm, model_path: "mlx-community/gemma-4-e4b-it-4bit" }
  max_tokens: 8192                  # raise for long, uncompressed output

outputs: [md, pdf]                  # formats to produce: md, pdf, prompt
                                    #   prompt = ready-to-paste prompt+transcript file (no API call)

output:
  subdir: ""                        # output/<subdir>/ ; empty = skill name
  stem_suffix: ""                   # <name><suffix>.<ext>
```

## Prompts and the transcript

Each prompt is plain Markdown. The transcript is injected at the
`[transcript]` (or `{transcript}`) placeholder if present; otherwise it is
appended to the end of the prompt. So either of these works:

```markdown
# Role
...instructions...

### transcript
[transcript]
```

```markdown
...instructions... (no placeholder → transcript appended automatically)
```

## Adding a new skill

1. Copy an existing folder: `cp -r skills/meeting-minutes skills/my-skill`
2. Edit `skill.yaml` (`name`, `description`, `defaults`, `outputs`, `output`).
3. Write your prompt(s) in `prompts/<lang>.md`.
4. Run: `uv run main.py input/file.mp4 --skill my-skill`

Use a different skills directory entirely with the `MINUTES_SKILLS_DIR`
environment variable.
