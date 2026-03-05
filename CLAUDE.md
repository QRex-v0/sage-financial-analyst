# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

Uses `uv` with a `.venv` virtual environment (Python 3.12).

Required `.env` variables:
- `ANTHROPIC_API_KEY` — picked up automatically by `Anthropic()`
- `HYPERBROWSER_API_KEY` — picked up automatically by `Hyperbrowser()`
- `EDGAR_IDENTITY` — required by SEC, format: `"Name email@example.com"`

```bash
uv pip install -r requirements.txt
uv run python basic.py
```

## Architecture

**`basic.py`** — Entry point. Runs a synchronous agentic loop: calls Claude Sonnet, processes `tool_use` blocks by dispatching to `run_tool`, appends `tool_result` messages, and loops until `stop_reason == "end_turn"`. Has a `MAX_WEB_FETCHES` constant to limit expensive page fetches per run. Retries on `RateLimitError` with a 60s sleep.

**`tools/__init__.py`** — Central tool registry. Exports `TOOLS` (the list passed to the API) and `run_tool(name, input, web_fetch_count)`. All new tools must be registered here in both places.

**`tools/hb.py`** — Hyperbrowser wrapper: `search(query)` and `web_fetch_and_summarize(url, instructions)`. The summarize variant calls `quant_analysis_summary` to extract only the relevant info before returning to the main model.

**`tools/sec.py`** — SEC EDGAR tools via `edgartools`. Uses `xbrl.get_statement_by_type()` for financial data (not `.income_statement()` — that method doesn't exist). TenK attributes are `.business` and `.management_discussion` (not `item_1`/`item_7`). TenQ uses `.get_item_with_part("Part I", "Item 2")` for MD&A.

**`tools/quant_analyst.py`** — MiniMax submodel that acts as a cheap page content extractor. Takes raw markdown content + specific extraction instructions, returns only what was asked for.

**`models/minimax.py`** — MiniMax API client.

## Key Design Decisions

- `web_fetch_and_summarize` replaced raw `web_fetch` as the exposed tool — raw pages are too large to feed directly to the main model
- `MAX_WEB_FETCHES` in `tools/__init__.py` controls how many page fetches are allowed per run (for cost/rate-limit control)
- The two-tier model pattern: Sonnet for reasoning, MiniMax for cheap data extraction
