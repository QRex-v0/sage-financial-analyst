import logging

from models.minimax import minimax_client

log = logging.getLogger(__name__)


# def quant_analyst(query: str) -> str:
# # ant.messages.create(....)
#     return "Quantitative analyst"


def quant_analysis_summary(content: str, instructions: str) -> str:
    response = minimax_client.messages.create(
        model="MiniMax-M2.5",
        max_tokens=1000,
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
    log.debug("🧠 MiniMax input | instructions: %s\n--- content ---\n%s", instructions, content)
    for block in response.content:
        if block.type == "thinking":
            log.info("[quant_analyst] 💭 thinking:\n%s", block.thinking)
            log.debug("[quant_analyst] 💭 thinking (full):\n%s", block.thinking)
        elif block.type == "text":
            log.info("[quant_analyst] 💬 text:\n%s", block.text)
            return block.text
    return "NOT FOUND: summarizer returned no text content."