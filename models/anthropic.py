from anthropic import Anthropic

_client = Anthropic()

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 1024


def chat(messages: list, system: str, tools: list, model: str = DEFAULT_MODEL, max_tokens: int = DEFAULT_MAX_TOKENS):
    return _client.messages.create(
        system=system,
        messages=messages,
        tools=tools,
        model=model,
        max_tokens=max_tokens,
    )
