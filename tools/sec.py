import os

from edgar.core import set_identity
from edgar.entity import Company
from edgar.company_reports import TenK, TenQ

set_identity(os.environ.get("EDGAR_IDENTITY", "Research Agent research@example.com"))


TICKER_MAP = dict[str, Company]() 

def _get_company(ticker: str) -> Company:
    if ticker not in TICKER_MAP:
        TICKER_MAP[ticker] = Company(ticker)
    return TICKER_MAP[ticker]


def _format_statement(stmt: dict) -> str:
    """Format a statement dict from get_statement_by_type into a readable table."""
    periods = stmt.get("periods", {})
    period_keys = list(periods.keys())
    period_labels = [periods[k]["label"] for k in period_keys]

    header = f"{'Line Item':<50} " + "  ".join(f"{lbl:>30}" for lbl in period_labels)
    rows = [header, "-" * len(header)]

    for item in stmt.get("data", []):
        if item.get("is_abstract"):
            rows.append(f"\n{item['label'].upper()}")
            continue
        if not item.get("has_values"):
            continue
        indent = "  " * item.get("level", 0)
        label = (indent + item["label"])[:50]
        values = item.get("values", {})
        unit = list(item.get("units", {}).values())[0] if item.get("units") else "usd"
        row = f"{label:<50}"
        for pk in period_keys:
            val = values.get(pk)
            if val is None:
                row += f"  {'N/A':>30}"
            elif unit == "usdPerShare":
                row += f"  {val:>30.2f}"
            else:
                row += f"  {val/1e9:>29.2f}B"
        rows.append(row)

    return "\n".join(rows)


def get_financials(ticker: str) -> str:
    """Income statement, balance sheet, and cash flow from the latest 10-K (XBRL)."""
    company = _get_company(ticker)
    filing = company.get_filings(form="10-K").latest(1)
    if not filing:
        return f"No 10-K found for {ticker}"

    xbrl = filing.xbrl()
    if not xbrl:
        return f"No XBRL data available for {ticker}'s latest 10-K (period: {filing.period_of_report})"

    sections = [f"# Financial Statements for {ticker} — Period: {filing.period_of_report}\n"]

    for label, stmt_type in [
        ("Income Statement", "IncomeStatement"),
        ("Balance Sheet", "BalanceSheet"),
        ("Cash Flow Statement", "CashFlowStatement"),
    ]:
        stmt = xbrl.get_statement_by_type(stmt_type)
        if stmt:
            sections.append(f"## {label}\n{_format_statement(stmt)}\n")

    return "\n".join(sections)


def get_annual_report(ticker: str) -> str:
    """Business overview (Item 1) and MD&A (Item 7) from the latest 10-K."""
    company = _get_company(ticker)
    filing = company.get_filings(form="10-K").latest(1)
    if not filing:
        return f"No 10-K found for {ticker}"

    ten_k = TenK(filing)
    period = filing.period_of_report

    parts = [f"# 10-K Annual Report for {ticker} — Period: {period}\n"]

    business = ten_k.business
    if business:
        parts.append(f"## Item 1: Business\n{business}\n")

    mda = ten_k.management_discussion
    if mda:
        parts.append(f"## Item 7: Management's Discussion and Analysis\n{mda}\n")

    if len(parts) == 1:
        return f"Could not extract narrative sections from {ticker}'s latest 10-K"

    return "\n".join(parts)


def get_quarterly_report(ticker: str) -> str:
    """MD&A from the latest 10-Q."""
    company = _get_company(ticker)
    filing = company.get_filings(form="10-Q").latest(1)
    if not filing:
        return f"No 10-Q found for {ticker}"

    ten_q = TenQ(filing)
    period = filing.period_of_report

    mda = ten_q.get_item_with_part("Part I", "Item 2")
    if not mda:
        return f"Could not extract MD&A from {ticker}'s latest 10-Q (period: {period})"

    return f"# 10-Q Quarterly Report for {ticker} — Period: {period}\n\n## Item 2: Management's Discussion and Analysis\n{mda}"


def get_recent_earnings(ticker: str) -> str:
    """Text of the most recent 8-K earnings press release."""
    company = _get_company(ticker)
    filings = company.get_filings(form="8-K").latest(5)
    if not filings:
        return f"No 8-K filings found for {ticker}"

    candidates = [filings] if not hasattr(filings, '__iter__') else filings
    for filing in candidates:
        text = filing.text()
        if text and any(kw in text.lower() for kw in ("earnings", "revenue", "net income", "quarterly results", "financial results")):
            return f"# 8-K Filing for {ticker} — Filed: {filing.filing_date}\n\n{text}"

    # Fall back to the most recent 8-K regardless
    filing = candidates[0]
    text = filing.text() or "No text content available"
    return f"# 8-K Filing for {ticker} — Filed: {filing.filing_date}\n\n{text}"
