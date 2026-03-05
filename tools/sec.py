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

    for label, stmt in [
        ("Income Statement", xbrl.income_statement()),
        ("Balance Sheet", xbrl.balance_sheet()),
        ("Cash Flow Statement", xbrl.cashflow_statement()),
    ]:
        if stmt:
            sections.append(f"## {label}\n{stmt.to_dataframe().to_string()}\n")

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

    business = ten_k.item_1
    if business:
        parts.append(f"## Item 1: Business\n{business}\n")

    mda = ten_k.item_7
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

    mda = ten_q.item_2
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
