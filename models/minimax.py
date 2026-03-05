from dotenv import load_dotenv
import os

from anthropic import Anthropic


load_dotenv()

BASE_URL = "https://api.minimax.io/anthropic"

# For MiniMax models (Anthropic-compatible)
minimax_client = Anthropic(
    api_key=os.environ.get("MINIMAX_API_KEY"),
    base_url=BASE_URL,
)