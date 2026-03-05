import logging
import time
from pathlib import Path

from dotenv import load_dotenv
from anthropic import RateLimitError

from utils.logging_setup import setup_logging, section
from models import chat, DEFAULT_MODEL, DEFAULT_MAX_TOKENS
from tools import TOOLS, run_tool

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)
run_prefix = setup_logging()

# --- Config ---
MODEL = DEFAULT_MODEL
MAX_TOKENS = DEFAULT_MAX_TOKENS
MAX_WEB_FETCHES = 1

QUERY = (
    "Do a comprehensive research on NVDA stock and make a buy/sell recommendation "
    "along with an equity research style report."
)

SYSTEM_PROMPT = (
    "You are a senior financial research analyst. When given a research request, "
    "you think carefully about what data you need before drawing conclusions. "
    "For any company or topic, you proactively gather: recent earnings reports and guidance, "
    "latest news and press releases, analyst ratings and price targets, macroeconomic or "
    "sector trends that are relevant, and any recent controversies or risks. "
    "Use the search tool to find relevant sources. For SEC filings, use the dedicated tools "
    "(get_financials, get_annual_report, get_quarterly_report, get_recent_earnings). "
    "To read a web page, use web_fetch_and_summarize — you must provide specific instructions "
    "describing exactly what information you want extracted from that page (e.g. 'Extract Q3 revenue, "
    "EPS, and forward guidance'). Do not use vague instructions like 'summarize this page'. "
    "Triangulate across multiple sources before forming a view. "
    "Present your findings in a structured equity research report with clear sections: "
    "executive summary, business overview, financial analysis, catalysts and risks, "
    "valuation, and a final buy/hold/sell recommendation with a price target rationale."
)

def save_report(report: str) -> None:
    report_path = Path(f"{run_prefix}_report.md")
    report_path.write_text(report)
    log.info("📝 Report saved to %s", report_path)


def main() -> None:
    messages = [{"role": "user", "content": QUERY}]
    turn = 0
    web_fetch_count = [0]

    log.info(
        "\n%s\n  RUN STARTED\n  Query      : %s\n  Model      : %s\n  Max fetches: %d\n%s",
        "=" * 60, QUERY, MODEL, MAX_WEB_FETCHES, "=" * 60,
    )

    while True:
        turn += 1
        section(f"TURN {turn}")

        while True:
            try:
                response = chat(
                    messages=messages,
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                )
                break
            except RateLimitError:
                log.warning("Rate limited, waiting 60s before retry...")
                time.sleep(60)

        log.info("🛑 stop_reason: %s", response.stop_reason)

        for block in response.content:
            if hasattr(block, "text") and block.text:
                log.info("🤖 Model:\n%s", block.text)
                log.debug("🤖 Model (full):\n%s", block.text)

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            section("FINAL REPORT")
            report = "\n".join(block.text for block in response.content if hasattr(block, "text"))
            print(report)
            save_report(report)
            break

        section(f"TURN {turn} — TOOL CALLS")
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input, web_fetch_count)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        if not tool_results:
            log.warning("⚠️  No tool results produced this turn — asking model to proceed with available data")
            messages.append({"role": "user", "content": "No additional data could be fetched. Please proceed with the information already gathered."})
        else:
            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    main()
