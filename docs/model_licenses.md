# モデル・ライブラリ ライセンス一覧

このツールが使用するモデルおよびライブラリのライセンス情報です。

**重要:** このツール自体は MIT ライセンスですが、**使用するモデルはそれぞれ独自のライセンスに従います。**  
商用利用・再配布を行う前に必ず各ライセンスの原文をご確認ください。

---

## このツール自体のライセンス

| 項目 | 内容 |
|-----|------|
| ライセンス | MIT |
| 著作権者 | Yuto Shimmyo (2025-2026) |
| ライセンス全文 | `LICENSE` ファイルを参照 |

---

## ASR（音声認識）モデル

### Whisper（OpenAI）

| モデル | プリセット | ライセンス | 配布元（HF モデルカード） |
|--------|-----------|-----------|--------|
| whisper-large-v3 | C（高品質） | **Apache-2.0** | [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) |
| whisper-large-v3-turbo | B/D（標準） | **MIT** | [openai/whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo) |
| whisper-medium | B/D（fallback）| **Apache-2.0** | [openai/whisper-medium](https://huggingface.co/openai/whisper-medium) |
| whisper-small | B/D（fallback）| **Apache-2.0** | [openai/whisper-small](https://huggingface.co/openai/whisper-small) |

> **ライセンスの帰属に関する注意（重要）:**
> - OpenAI のオリジナル Whisper（[GitHub](https://github.com/openai/whisper) のコード＆重み）は **MIT**。
> - 一方、HuggingFace 上の `openai/*` モデルカードの license タグは **Apache-2.0**（ただし `whisper-large-v3-turbo` のみ **MIT**）。上表は HF のモデルカードに準拠した値です。
> - 本ツールの `faster-whisper` は上記をそのまま使うのではなく、**CTranslate2 形式に変換された再配布版**（例: [`Systran/faster-whisper-large-v3`](https://huggingface.co/Systran/faster-whisper-large-v3) / [`Systran/faster-whisper-medium`](https://huggingface.co/Systran/faster-whisper-medium)、turbo は [`mobiuslabsgmbh/faster-whisper-large-v3-turbo`](https://huggingface.co/mobiuslabsgmbh/faster-whisper-large-v3-turbo) 等）を自動取得します。これらの再配布版は **MIT** です。

- **MIT / Apache-2.0 のいずれも、商用利用・改変・再配布が可能**（著作権表示・ライセンス表示を保持すること）。

---

### NVIDIA Parakeet TDT（プリセット A）

| モデル | ライセンス | 配布元 |
|--------|-----------|--------|
| parakeet-tdt-0.6b-v2 | **CC-BY-4.0** | [nvidia/parakeet-tdt-0.6b-v2](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2) |

**CC-BY-4.0 の主な条件:**

| 行為 | 条件 |
|-----|------|
| 推論（個人・研究利用） | 自由に使用可（帰属表示不要） |
| 成果物の公開・論文掲載 | NVIDIA への帰属表示が必要 |
| モデルの再配布・改変 | 帰属表示 + CC-BY-4.0 ライセンス表示が必要 |
| 商用利用 | 可（帰属表示が必要） |

**帰属表示の例（再配布・公開時）:**
```
This product uses NVIDIA Parakeet TDT 0.6B v2.
Model: https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2
License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
```

- Parakeet は**英語専用**。日本語音声には使用不可。
- ライセンス全文: https://creativecommons.org/licenses/by/4.0/

---

## 議事録生成（LLM）モデル

### OpenAI ChatGPT（API・推奨）

| モデル | ライセンス形態 | 配布元 |
|--------|------------|--------|
| gpt-5.5 など | OpenAI API / Business Terms | [OpenAI Platform](https://platform.openai.com/) |

- モデル自体は配布されない（API 経由での利用のみ）。最も高品質で、本ツールの推奨プロバイダ。
- 利用規約: https://openai.com/policies/ — 商用利用・データ取り扱いの条件を事前に確認すること。
- モデル名（`gpt-5.5` 等）は `config.yaml` / `skill.yaml` で設定可能。

---

### Gemma 4 E4B（ローカル推奨・mlx-vlm）

| モデル | ライセンス | 配布元 |
|--------|-----------|--------|
| gemma-4-e4b-it（4bit量子化） | **Apache-2.0** | [mlx-community/gemma-4-e4b-it-4bit](https://huggingface.co/mlx-community/gemma-4-e4b-it-4bit) |

- Gemma 4 は Google が 2026年に **Apache 2.0 で公開**（Gemma 1/2/3 の独自ライセンス「Gemma Terms of Use」から変更）
- **商用利用・改変・再配布が可能**（著作権表示・ライセンス表示を保持すること）
- モデルを再配布する場合、`NOTICE` ファイルが含まれていればその保持が必要（Apache 2.0 第4条）
- 元モデル: https://huggingface.co/google/gemma-4-E4B-it
- ライセンス全文: https://www.apache.org/licenses/LICENSE-2.0

---

### Qwen 2.5（mlx-lm）

| モデル | ライセンス | 配布元 |
|--------|-----------|--------|
| Qwen2.5-7B-Instruct（4bit）| **Apache 2.0** | [mlx-community/Qwen2.5-7B-Instruct-4bit](https://huggingface.co/mlx-community/Qwen2.5-7B-Instruct-4bit) |

- **商用利用・改変・再配布が可能**（著作権表示・ライセンス表示を保持すること）
- ライセンス全文: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/main/LICENSE

---

### Gemma 3（mlx-lm / Ollama、代替モデル）

| モデル | ライセンス | 配布元 |
|--------|-----------|--------|
| gemma-3-4b-it | **Gemma Terms of Use** | [mlx-community/gemma-3-4b-it-4bit](https://huggingface.co/mlx-community/gemma-3-4b-it-4bit) |
| gemma2:9b（Ollama）| **Gemma Terms of Use** | [Ollama library](https://ollama.com/library/gemma2) |

- Gemma 1/2/3 は Google の独自ライセンス（Gemma Terms of Use）に従う
- **商用利用には条件あり**（月間アクティブユーザー 2,000万人未満は原則無料）
- ライセンス全文: https://ai.google.dev/gemma/terms

---

### Google Gemini（API）

| モデル | ライセンス形態 | 配布元 |
|--------|------------|--------|
| gemini-2.5-flash | Google API Terms of Service | [Google AI Studio](https://aistudio.google.com/) |
| gemini-2.5-flash-lite | Google API Terms of Service | [Google AI Studio](https://aistudio.google.com/) |
| gemini-2.0-flash | Google API Terms of Service | [Google AI Studio](https://aistudio.google.com/) |

- モデル自体は配布されない（API 経由での利用のみ）
- 利用規約: https://ai.google.dev/gemini-api/terms
- 無料枠の範囲と商用利用の条件を事前に確認すること

---

## Python ライブラリのライセンス

このツールが依存するライブラリのライセンスです。

| ライブラリ | ライセンス | 用途 |
|-----------|-----------|------|
| faster-whisper | **MIT** | Whisper 音声認識バックエンド |
| mlx-lm | **MIT** | Apple Silicon 向けテキスト LLM 推論 |
| mlx-vlm | **MIT** | Apple Silicon 向けマルチモーダル LLM 推論 |
| google-genai | **Apache 2.0** | Gemini API クライアント |
| openai | **Apache 2.0** | OpenAI / ChatGPT API クライアント |
| huggingface-hub | **Apache 2.0** | モデルのダウンロード管理 |
| python-dotenv | **BSD 3-Clause** | 環境変数（.env）読み込み |
| pyyaml | **MIT** | YAML 設定ファイル読み込み |
| markdown | **BSD 3-Clause** | Markdown → HTML 変換（PDF 出力用） |
| weasyprint | **BSD 3-Clause** | HTML → PDF レンダリング（PDF 出力用） |

---

## コンプライアンスチェックリスト

このツールを使用する際に確認すること：

- [ ] **モデルを再配布しない**（`models/` は `.gitignore` で除外済み）
- [ ] **Parakeet を公開成果物に使う場合**は NVIDIA への帰属表示を追加する
- [ ] **Gemma 3/Gemma 2** を商用利用する場合は Google の利用規約を確認する
- [ ] **Gemini API** を商用利用する場合は Google API Terms of Service を確認する
- [ ] **OpenAI / ChatGPT API** を商用利用する場合は OpenAI の利用規約を確認する
- [ ] **Apache 2.0 モデル（Gemma 4, Qwen2.5, Whisper large-v3/medium/small）** を改変・再配布する場合は著作権・ライセンス表示を保持する

---

## 免責事項

- このツールはモデル本体を同梱・配布しません。
- モデルのダウンロード・使用はユーザーの責任で行ってください。
- ライセンス条件は変更される場合があります。利用前に必ず原文を確認してください。
