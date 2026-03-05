# Sage

An AI-powered equity research agent. Give it a stock ticker and it produces a structured buy/hold/sell report by autonomously gathering data from the web and SEC filings.

## How it works

The main model (Claude Sonnet) runs an agentic loop — it decides what data to fetch, calls tools, reads the results, and iterates until it has enough information to write a full research report. A secondary model (MiniMax) acts as a cheap preprocessor that extracts specific information from raw web pages before sending results back to the main model, keeping token costs down.

## Tools available to the agent

| Tool | Source | What it fetches |
|---|---|---|
| `search` | Hyperbrowser | Web search results |
| `web_fetch_and_summarize` | Hyperbrowser + MiniMax | Fetches a page, extracts specific info |
| `get_financials` | SEC EDGAR (XBRL) | Income statement, balance sheet, cash flow |
| `get_annual_report` | SEC EDGAR 10-K | Business overview + MD&A |
| `get_quarterly_report` | SEC EDGAR 10-Q | Latest quarterly MD&A |
| `get_recent_earnings` | SEC EDGAR 8-K | Most recent earnings press release |

## Setup

**1. Install dependencies**
```bash
uv pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp .env.example .env
```

Fill in `.env`:
```
ANTHROPIC_API_KEY=...
HYPERBROWSER_API_KEY=...
EDGAR_IDENTITY=Your Name your.email@example.com
```

`EDGAR_IDENTITY` is required by the SEC — use your real name and email.

**3. Run**
```bash
uv run python basic.py
```

## Project structure

```
basic.py          # Agent loop — orchestrates the main model and tool calls
tools/
  __init__.py     # Tool registry (TOOLS list + run_tool dispatcher)
  hb.py           # Hyperbrowser: web search and page fetch
  sec.py          # SEC EDGAR: 10-K, 10-Q, 8-K data via edgartools
  quant_analyst.py # MiniMax submodel: summarizes raw page content
models/
  minimax.py      # MiniMax API client
```
