# Recording → Artifact Platform

自分で録音した音声・動画を、用途ごとの **スキル** で **所望の形式（Markdown / PDF）** に変換するツールです。
会議の議事録、マジックのレクチャーノートなど、**コードを書かずにスキルを足して**いける拡張可能なプラットフォームです。
日本語・英語どちらにも対応します。

```bash
# 文字起こしのみ（最速）
uv run main.py input/meeting.mp4

# 会議 → 議事録（既定スキル）
uv run main.py input/meeting.mp4 --minutes-backend api

# マジック動画 → 詳細な日本語レクチャーノート + PDF
uv run main.py input/talk.mp4 --skill magic-lecture --output md,pdf

# 文字起こし + 貼り付け用プロンプトだけ生成（API課金ゼロ）
uv run main.py input/talk.mp4 --skill magic-lecture --output prompt
```

---

## できること

| 機能 | 説明 |
|------|------|
| 🎙️ 音声認識 (STT) | Whisper / Parakeet による高精度文字起こし（日・英・自動検出） |
| 🧩 スキル（用途） | `skills/<名前>/` を置くだけで新しい用途を追加。プロンプトもここで一元管理 |
| 📝 生成（API / ローカル） | ChatGPT / Gemini（API）または mlx・Ollama（ローカル）で生成 |
| 📄 出力フォーマット | Markdown / PDF（WeasyPrint、日本語フォント対応）/ コピペ用プロンプトをプラガブルに出力 |
| 💸 API課金ゼロ運用 | `--output prompt` で「プロンプト＋文字起こし」を生成し、ChatGPT 等へ手貼りできる |
| 🌐 言語別プロンプト | 音声言語（日/英）に応じてプロンプトを自動切替（スキルで固定も可） |
| 🖥️ リモート実行 | 重い処理・多数バッチを Slurm クラスタへデプロイして実行 |

> **生成バックエンドのおすすめ:** **ChatGPT（OpenAI, 例: `gpt-5.5`）が最も高品質で推奨**です。
> 次点で Gemini、完全オフラインなら mlx（Apple Silicon）/ Ollama を使います。

---

## セットアップ

```bash
# uv（パッケージ管理）
curl -LsSf https://astral.sh/uv/install.sh | sh

# ffmpeg（音声変換）
brew install ffmpeg            # macOS
# sudo apt install ffmpeg      # Ubuntu/Debian

# PDF 出力を使う場合のシステムライブラリ（WeasyPrint 用）
brew install pango cairo gdk-pixbuf libffi   # macOS

# 依存パッケージ
uv sync
```

> PDF は加点機能です。上記システムライブラリが無くても Markdown 出力は動作し、PDF だけが
> 親切なエラーで無効化されます（`--output md` でも回避可）。macOS(Apple Silicon) では Homebrew の
> ライブラリパスを自動で解決します。

### API キー

```bash
cp .env.template .env
# .env を編集して使うキーを設定:
#   OPENAI_API_KEY=...   ← ChatGPT（推奨）  https://platform.openai.com/api-keys
#   GEMINI_API_KEY=...   ← Gemini（代替）   https://aistudio.google.com/app/apikey
```

---

## スキル（用途）

スキルは「録音を何に変換するか」のレシピです。一覧表示:

```bash
uv run main.py --list-skills
```

同梱スキル:

| スキル | 用途 | 既定の出力 |
|--------|------|-----------|
| `meeting-minutes` | 構造化された議事録（既定） | `output/minutes/<name>_minutes.md` |
| `magic-lecture` | マジック動画の詳細な日本語レクチャーノート（常に日本語） | `output/magic-lecture/<name>.md` + `.pdf` |

新しいスキルは `skills/<名前>/`（`skill.yaml` + `prompts/<lang>.md`）を作るだけで追加できます。
詳細は [skills/README.md](skills/README.md) を参照してください。プロンプトはすべてここで一元管理されます。

---

## API 課金ゼロで ChatGPT に貼る（`--output prompt`）

API 料金をかけたくないときは、`prompt` 出力でスキルのプロンプトに文字起こしを差し込んだ
**「そのまま貼れる完成プロンプト」** をファイル化できます。**API は一切呼びません。**

```bash
uv run main.py input/talk.mp4 --skill magic-lecture --output prompt
# → output/magic-lecture/<name>_prompt.txt （プロンプト全文 + 文字起こし）
```

生成された `.txt` を ChatGPT 等の Web UI に貼り付けて推論させてください。
`--output prompt,md` のように生成系と併用も可能です。

---

## CLI の使い方

```bash
uv run main.py <音声ファイル> [オプション]
```

| オプション | 選択肢 / 例 | 説明 |
|-----------|-------------|------|
| `--skill` | `meeting-minutes` / `magic-lecture` / … | 用途（レシピ）。既定: meeting-minutes |
| `--list-skills` | — | 利用可能なスキルを一覧表示 |
| `--output` | `md` / `pdf` / `prompt`（カンマ区切り可） | 出力フォーマット（既定はスキル依存） |
| `--minutes-provider` | `openai` / `gemini` | API プロバイダ（既定はスキル/config。openai 推奨） |
| `--language` | `ja` / `en` / `auto` | 音声言語（既定: auto） |
| `--profile` | `fast` / `standard` / `quality` | 品質プロファイル（既定: standard） |
| `--asr-preset` | `A` / `B` / `C` / `D` | ASR プリセット（下記参照） |
| `--asr-backend` | `faster_whisper` / `parakeet` | ASR バックエンドを強制指定 |
| `--asr-model` | `large-v3` など | ASR モデルを強制指定 |
| `--minutes-backend` | `none` / `api` / `local` | 生成バックエンド（既定はスキル依存。none=文字起こしのみ） |
| `--minutes-model` | モデル名 | 生成モデル（API モデル名 / HuggingFace ID / ローカルパス） |
| `--minutes-local-runtime` | `mlx-vlm` / `mlx-lm` / `ollama` | ローカル LLM ランタイム |
| `--minutes-language` | `ja` / `en` / `auto` | プロンプト/出力言語の上書き（auto=スキルに従う） |
| `--minutes-max-tokens` | 整数 | 生成トークン上限の上書き（既定はスキル依存） |
| `--config` | パス | config.yaml のパス |

### 優先順位

設定は次の順で上書きされます（右ほど強い）:

```text
コード既定  <  config.yaml  <  skill.yaml の defaults  <  CLI オプション
```

---

## ASR プリセットの選び方

| プリセット | 言語 | 品質 | モデル | 備考 |
|-----------|------|------|--------|------|
| **A** | 英語 | 高品質 | Parakeet TDT → Whisper large-v3 | Parakeet は英語専用 |
| **B** | 英語 | 標準 | Whisper large-v3-turbo | 速度と品質のバランス |
| **C** | 多言語 | 高品質 | Whisper large-v3 | 日本語にも最適 |
| **D** | 多言語 | 標準 | Whisper large-v3-turbo | デフォルト（推奨） |

| `--profile` | `--language` | 選択されるプリセット |
|------------|-------------|------------------|
| quality | en | A |
| standard | en | B |
| quality | ja | C |
| standard | ja | D |
| * | auto | C (quality) / D (standard/fast) |

---

## config.yaml

`config.yaml` で既定値を一元管理し、`skill.yaml` と CLI で上書きします。

```yaml
profile: standard         # fast / standard / quality
language: auto            # auto / ja / en（音声の言語）

skill:
  name: meeting-minutes   # 既定スキル
  # outputs: [md, pdf]    # スキル既定を上書きしたい場合

asr:
  preset: auto            # auto / A / B / C / D
  backend: ""             # 空=自動 / faster_whisper / parakeet
  model: ""               # 空=自動 / large-v3 / medium / small など

minutes:
  backend: none           # none / api / local
  output_language: auto   # auto=音声言語に追従 / ja / en
  max_tokens: 2048        # 生成トークン上限（スキルが引き上げ可）
  api:
    provider: openai      # openai（ChatGPT, 推奨）/ gemini
    model: gpt-5.5
  local:
    runtime: mlx-vlm      # mlx-vlm / mlx-lm / ollama
    model_path: "mlx-community/gemma-4-e4b-it-4bit"
    ollama_model: "gemma2:9b"
    ollama_url: "http://localhost:11434"
```

---

## リモート実行（Slurm）

重い ASR や多数のファイルをまとめて処理したいときは、Slurm クラスタへデプロイして実行できます。

```bash
# input/talk.mp4 を転送し、magic-lecture スキルでジョブ投入
python deploy.py input/talk.mp4 user@cc21dev0 --remote_dir my_job -- \
    --skill magic-lecture --minutes-backend api --output md
```

`--` 以降の引数は、クラスタ上の `main.py` にそのまま渡されます（[scripts/run_slurm.sh](scripts/run_slurm.sh)）。
スキル・プロンプトも自動で転送されます。クラスタでは mlx は使えないため API か faster_whisper を、
PDF はシステムライブラリが無ければ `--output md` を推奨します。

---

## 出力ファイル

| ファイル | 説明 |
|---------|------|
| `output/transcripts/<name>.txt` | 文字起こしテキスト（全スキル共通） |
| `output/<skill>/<name>.md` / `.pdf` | スキルが生成した成果物。meeting-minutes は `output/minutes/<name>_minutes.md` |
| `output/<skill>/<name>_prompt.txt` | `--output prompt` で出力する貼り付け用プロンプト（API 不使用） |

対応フォーマット（入力）: `.m4a`, `.mp3`, `.mp4`, `.wav`, `.flac`, `.ogg`, `.webm` など ffmpeg が扱える形式すべて。

---

## よくあるエラー

- **`File not found`** — 入力パスを確認（`input/` 配置推奨）。
- **`OPENAI_API_KEY is not set` / `GEMINI_API_KEY is not set`** — `.env` にキーを設定。
- **PDF: `WeasyPrint is unavailable`** — `brew install pango cairo gdk-pixbuf libffi`、または `--output md`。
- **`Cannot connect to Ollama`** — `ollama serve` と `ollama pull <model>`。
- **`mlx-* requires Apple Silicon`** — 他環境では `--minutes-backend api` か `--minutes-local-runtime ollama`。
- **生成が途中で切れる** — `--minutes-max-tokens` を増やす（長文スキルは `skill.yaml` で既定を引き上げ済み）。

---

## ライセンス

このツール自体は MIT ライセンスです。使用するモデルは各モデルのライセンスに従います。
商用利用の前に [docs/model_licenses.md](docs/model_licenses.md) を確認してください。

---

## ディレクトリ構成

```text
.
├── main.py                 # エントリポイント（ASR → 生成 → エクスポート）
├── config.yaml             # 既定設定
├── skills/                 # スキル（用途）。プロンプトもここで一元管理
│   ├── meeting-minutes/    #   skill.yaml + prompts/{ja,en}.md
│   ├── magic-lecture/      #   skill.yaml + prompts/ja.md（[transcript] プレースホルダ）
│   └── README.md           #   スキル追加手順
├── src/
│   ├── config.py           # 設定の読込・優先順位マージ
│   ├── prompts.py          # プロンプト読込 + transcript 注入（render_prompt）
│   ├── skills.py           # スキルローダー
│   ├── asr/                # 音声認識バックエンド（faster_whisper / parakeet）
│   ├── summarizer/         # 生成バックエンド（openai / gemini / mlx-vlm / mlx-lm / ollama）
│   └── exporters/          # 出力フォーマット（markdown / pdf-weasyprint / prompt）
├── deploy.py               # Slurm へのデプロイ
├── scripts/run_slurm.sh    # クラスタ実行スクリプト
├── input/                  # 入力（Git 除外）
└── output/                 # 出力（Git 除外）
```
