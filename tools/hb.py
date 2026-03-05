from dotenv import load_dotenv
from hyperbrowser import Hyperbrowser
from hyperbrowser.models import FetchParams, FetchOutputOptions, WebSearchParams
from tools.quant_analyst import quant_analysis_summary

load_dotenv()

_client = Hyperbrowser()

def search(query: str):
    resp = _client.web.search(WebSearchParams(query=query))
    return str(resp.data.results)

def web_fetch(url: str):
    resp = _client.web.fetch(FetchParams(url=url, stealth="auto", outputs=FetchOutputOptions(formats=["markdown"])))
    return resp.data.markdown or f"Failed to fetch {url}"

def web_fetch_and_summarize(url: str, instructions: str):
    resp_md = web_fetch(url)
    if resp_md.startswith("Failed to fetch"):
        return resp_md
    return quant_analysis_summary(resp_md, instructions)