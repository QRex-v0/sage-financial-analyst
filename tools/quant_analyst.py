import logging

from models.minimax import client, DEFAULT_MODEL, DEFAULT_MAX_TOKENS

log = logging.getLogger(__name__)


def quant_analysis_summary(content: str, instructions: str) -> str:
    log.debug("🧠 MiniMax input | instructions: %s\n--- content ---\n%s", instructions, content)
    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=DEFAULT_MAX_TOKENS,
        system=(
            "You are a financial data extractor. You are given the raw text content of a webpage "
            "and a specific extraction instruction. Your job is to extract exactly what is requested "
            "and return it concisely. Do not add commentary, opinions, or information beyond what was asked. "
            "If the requested information is not present in the content, respond with: "
            "'NOT FOUND: <brief reason why>.'"
        ),
        messages=[
            {
                "role": "user",
                "content": f"INSTRUCTIONS: {instructions}\n\n---\n\nPAGE CONTENT:\n{content}"
            }
        ]
    )
    for block in response.content:
        if block.type == "thinking":
            log.info("[quant_analyst] 💭 thinking:\n%s", block.thinking)
            log.debug("[quant_analyst] 💭 thinking (full):\n%s", block.thinking)
        elif block.type == "text":
            log.info("[quant_analyst] 💬 text:\n%s", block.text)
            return block.text
    return "NOT FOUND: summarizer returned no text content."
