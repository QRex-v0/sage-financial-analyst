# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

This project uses `uv` as the Python package manager with a `.venv` virtual environment (Python 3.12).

Required environment variables (via `.env` file):
- `ANTHROPIC_API_KEY` — Claude API key (used by `AsyncAnthropic()` automatically)
- `HYPERBROWSER_API_KEY` — Hyperbrowser API key (used by `AsyncHyperbrowser()` automatically)

Run the main script:
```
uv run python basic.py
```

## Architecture

**`basic.py`** — Entry point. Creates an `AsyncAnthropic` client, defines two Claude tools (`search`, `web_fetch`), and invokes the model with a user prompt. The model uses tools iteratively to research and respond.

**`tools/hb.py`** — Thin async wrapper around the `hyperbrowser` library. Provides:
- `search(query)` — Web search via `AsyncHyperbrowser.web.search()`
- `web_fetch(url)` — Page fetch with stealth mode, returns markdown content

## Tool Use Pattern

`basic.py` uses Claude's tool use feature but does **not** implement an agentic loop — it makes a single API call and prints the raw response JSON. To handle multi-turn tool use (where Claude calls tools and the results feed back into the conversation), an agentic loop must be added that processes `tool_use` content blocks, calls the corresponding functions in `tools/hb.py`, and sends `tool_result` messages back.

The `system` prompt in `basic.py` is currently a placeholder (`"QINYU FILL OUT"`).
