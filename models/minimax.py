import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get("MINIMAX_API_KEY"),
    base_url="https://api.minimax.io/anthropic",
)
DEFAULT_MODEL = "MiniMax-M2.5"
DEFAULT_MAX_TOKENS = 2048
