# from models.anthropic import client, DEFAULT_MODEL, DEFAULT_MAX_TOKENS
from models.minimax import client, DEFAULT_MODEL, DEFAULT_MAX_TOKENS


def chat(messages: list, system: str, tools: list, model: str = DEFAULT_MODEL, max_tokens: int = DEFAULT_MAX_TOKENS):
    return client.messages.create(
        system=system,
        messages=messages,
        tools=tools,
        model=model,
        max_tokens=max_tokens,
    )
