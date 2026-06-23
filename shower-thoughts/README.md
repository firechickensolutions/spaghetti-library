# Shower Thoughts

Push a button. Speak a thought. Get a coherent Markdown note you can actually search later. **100% local** — the audio never leaves your machine.

A small Windows-style floating mic panel (think of the `Win+H` dictation bar): tap the mic, talk, tap again. It transcribes the whole thought in one pass, cleans it up, writes a dated note to your vault, indexes it for semantic search, and opens it. No terminal, no `cd`, no chasing files.

> Built and tested on **Windows 11** with an RTX 3080 Ti. The capture stack uses WASAPI (via PyAudioWPatch), so it's **Windows-only** as written. The pipeline itself (STT → note → index) is portable; the mic capture and the launcher are the Windows-specific parts.

## Why

The good thoughts show up away from the keyboard. By the time you sit down they're gone, or they're a cryptic half-line in a notes app. This captures the whole thought as you say it, turns it into something readable, and makes it findable — without making you stop and type.

## What you get per capture

- A **verbatim transcript** (your words, one coherent pass — no chopping).
- A note written to your vault as plain Markdown + YAML frontmatter (Obsidian-ready).
- A semantic index entry so you can later ask *"what did I think about X"* and get your own past reasoning back.

## Install

Requires **Python 3.11+**, a microphone, and [Ollama](https://ollama.com) running.

```bash
git clone https://github.com/firechickensolutions/spaghetti-library.git
cd spaghetti-library/shower-thoughts

pip install -e .                     # CPU (default, ~13x real-time)
# pip install -e .[gpu]              # optional GPU decode (see note below)

ollama pull qwen2.5:7b               # enrich: summary + structure
ollama pull nomic-embed-text         # embed: semantic search
```

The Parakeet speech model downloads automatically on first run.

### Models — what I used

These are what I ran on an **RTX 3080 Ti** and found worked best; treat them as a sensible baseline, not a hard requirement. Smaller machines can drop to lighter models.

| Role | Model | Runtime | Notes |
|---|---|---|---|
| Speech-to-text | `nemo-parakeet-tdt-0.6b-v3` | onnx-asr, **CPU** | ~13x real-time; doesn't hallucinate on silence; punctuates |
| Enrich (summary) | `qwen2.5:7b` | Ollama | summary + structure on top of the transcript |
| Embed (search) | `nomic-embed-text` | Ollama | 768-dim vectors, cosine search over SQLite |

Ollama isn't strictly required to get a note — if it's not running, the transcript still saves; you just don't get the enrich + search layer that run.

## The button (global hotkey)

```powershell
powershell -ExecutionPolicy Bypass -File install_shortcut.ps1
# or pick your own key:
powershell -ExecutionPolicy Bypass -File install_shortcut.ps1 -Hotkey "CTRL+ALT+J"
```

This installs a Start Menu shortcut with a **global hotkey** (default `Ctrl+Alt+T`). Press it from anywhere → the panel appears bottom-center → tap the mic → speak → tap to stop → your note opens. You can also pin "Shower Thoughts" from the Start Menu to your taskbar.

> Windows shortcut hotkeys must be `Ctrl+Alt+<key>`. For a true `Win+`-style key, use [AutoHotkey](https://www.autohotkey.com/) to launch `pythonw tools\capture_overlay.py`.

## Usage without the overlay (CLI)

```bash
python tools/capture_session.py                       # speak, Ctrl-C to stop -> note written + indexed
python -m thought_capture.query_cli "what did I decide about X" [-k N]
```

## Where notes go

By default, notes land in `~/ShowerThoughts`. To make them part of an existing **Obsidian** vault, point the vault path at a subfolder of your vault:

```
SHOWER_CAPTURE_VAULT_PATH=C:\Users\you\ObsidianVault\ShowerThoughts
```

Then just open that vault in Obsidian — the notes are plain Markdown, no plugin needed. The `.library/` folder (index + vocab) sits beside the notes; Obsidian ignores it.

## Your own names

Coined names (products, people, projects) get mis-heard by any STT. Ships empty — add yours:

```python
from thought_capture.vocab import add_term, add_correction
add_term("Photerra")                    # primes the LLM to spell it right
add_correction("photera", "Photerra")   # fixes an exact mis-hear in the raw text
```

Corrections are exact whole-token matches on non-words only, so they can never rewrite a real English word.

## How it works

```
mic ─► capture (.pcm on disk, crash-safe) ─► Parakeet STT (chunked for long captures)
     ─► exact mis-hear corrections ─► Markdown note written to the vault
     ─► Ollama enrich (summary/structure) + embed ─► SQLite vector store
     ─► query_cli "question" ─► cosine top-k over your own past thinking
```

The transcript note is the floor: it's written and durable before the (best-effort) enrich + index step, and a crash mid-capture recovers the audio into a note on the next launch.

## Config

All optional — see `.env.example`. Defaults work out of the box.

## License

See [LICENSE](LICENSE).
