from logging import getLogger

from anthropic.types import ToolParam
from tools.hb import search, web_fetch_and_summarize
from tools.sec import get_financials, get_annual_report, get_quarterly_report, get_recent_earnings

MAX_WEB_FETCHES = 1

log = getLogger(__name__)

TOOLS: list[ToolParam] = [
    {
        "type": "custom",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The query to search for"}
            }
        },
        "name": "search",
        "description": "Search the web for information",
    },
    {
        "type": "custom",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to fetch"},
                "instructions": {"type": "string", "description": "What specific information to extract from the page, e.g. 'Extract Q3 revenue, EPS, and forward guidance'"},
            },
            "required": ["url", "instructions"]
        },
        "name": "web_fetch_and_summarize",
        "description": "Fetch a web page and extract specific information from it. Specify exactly what you are looking for in the instructions.",
    },
    {
        "type": "custom",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. NVDA"}
            },
            "required": ["ticker"]
        },
        "name": "get_financials",
        "description": "Get income statement, balance sheet, and cash flow from the company's latest 10-K SEC filing",
    },
    {
        "type": "custom",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. NVDA"}
            },
            "required": ["ticker"]
        },
        "name": "get_annual_report",
        "description": "Get the business overview (Item 1) and management discussion & analysis (Item 7) from the latest 10-K SEC filing",
    },
    {
        "type": "custom",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. NVDA"}
            },
            "required": ["ticker"]
        },
        "name": "get_quarterly_report",
        "description": "Get management discussion & analysis from the latest 10-Q SEC filing (more recent than the annual report)",
    },
    {
        "type": "custom",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. NVDA"}
            },
            "required": ["ticker"]
        },
        "name": "get_recent_earnings",
        "description": "Get the most recent earnings press release from SEC 8-K filings",
    },
]


def run_tool(name: str, input: dict, web_fetch_count: list) -> str:
    if name == "search":
        log.info("  >> search: %s", input["query"])
        result = search(input["query"])
    elif name == "web_fetch_and_summarize":
        if web_fetch_count[0] >= MAX_WEB_FETCHES:
            log.info("  >> web_fetch_and_summarize SKIPPED (limit %d reached): %s", MAX_WEB_FETCHES, input["url"])
            return f"Skipped fetching {input['url']} (web_fetch limit of {MAX_WEB_FETCHES} reached)"
        web_fetch_count[0] += 1
        log.info("  >> web_fetch_and_summarize [%d/%d]: %s | instructions: %s", web_fetch_count[0], MAX_WEB_FETCHES, input["url"], input["instructions"])
        result = web_fetch_and_summarize(input["url"], input["instructions"])
    elif name == "get_financials":
        log.info("  >> get_financials: %s", input["ticker"])
        result = get_financials(input["ticker"])
    elif name == "get_annual_report":
        log.info("  >> get_annual_report: %s", input["ticker"])
        result = get_annual_report(input["ticker"])
    elif name == "get_quarterly_report":
        log.info("  >> get_quarterly_report: %s", input["ticker"])
        result = get_quarterly_report(input["ticker"])
    elif name == "get_recent_earnings":
        log.info("  >> get_recent_earnings: %s", input["ticker"])
        result = get_recent_earnings(input["ticker"])
    else:
        return f"Unknown tool: {name}"
    log.info("  << result: %d chars | preview: %s", len(result), result[:200].replace("\n", " ") + ("..." if len(result) > 200 else ""))
    return result
