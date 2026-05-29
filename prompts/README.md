# Prompts (fallback / default)

> **プロンプトは原則 `skills/<名前>/prompts/` で管理します。** 用途ごとのプロンプトは
> 各スキルのフォルダにあります（[../skills/README.md](../skills/README.md) を参照）。

このトップレベルの `prompts/` は、スキルを使わずに `load_prompt()` を直接呼んだ場合の
**フォールバック用デフォルト**です（`ja.md` / `en.md`）。通常は編集する必要はありません。

## プロンプトの選ばれ方（スキル経由）

選択基準は **レクチャー（音声）の言語** です（スキルが `prompt.language: fixed` の場合は固定）。

1. `--language ja` / `--language en` で明示、または
2. `--language auto`（既定）なら Whisper が検出した音声言語

に対応する `prompts/<lang>.md` が読み込まれ、対応ファイルが無ければ既定言語へフォールバックします。
出力言語を音声と別にしたい場合は `--minutes-language ja|en` で上書きできます。

## transcript の挿入

プロンプト内に `[transcript]` / `{transcript}` があればその位置へ書き起こしが挿入され、
無ければ末尾に連結されます（`src/prompts.py` の `render_prompt`）。

別フォルダのプロンプトを使う場合は環境変数でフォルダを差し替えられます:

- `MINUTES_SKILLS_DIR` … スキルのルート（`skills/`）
- `MINUTES_PROMPTS_DIR` … このフォールバック `prompts/`
