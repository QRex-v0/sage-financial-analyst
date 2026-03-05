import logging
import time

from dotenv import load_dotenv
from anthropic import Anthropic, RateLimitError
from tools import TOOLS, run_tool


load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

def section(title: str):
    log.info("\n%s\n  %s\n%s", "=" * 60, title, "=" * 60)

ant = Anthropic()

MAX_WEB_FETCHES = 1



def main():
    messages = [{"role": "user", "content": "Do a comprehensive research on NVDA stock and make a buy/sell recommendation along with an equity research style report."}]
    turn = 0
    web_fetch_count = [0]

    while True:
        turn += 1
        section(f"TURN {turn}")
        while True:
            try:
                response = ant.messages.create(
                    system=(
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
                    ),
                    messages=messages,
                    tools=TOOLS,
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                )
                break
            except RateLimitError:
                log.warning("Rate limited, waiting 60s before retry...")
                time.sleep(60)
        log.info("stop_reason: %s", response.stop_reason)

        for block in response.content:
            if hasattr(block, "text") and block.text:
                log.info("[ model ]\n%s", block.text)

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            section("FINAL REPORT")
            for block in response.content:
                if hasattr(block, "text"):
                    print(block.text)
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

        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    main()
