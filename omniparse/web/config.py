"""
Title: OmniParse
Author: Adithya S K
Date: 2024-07-02

This code includes portions of code from the crawl4ai repository by unclecode, licensed under the Apache 2.0 License.
Original repository: https://github.com/unclecode/crawl4ai

Original Author: unclecode

License: Apache 2.0 License
URL: https://github.com/unclecode/crawl4ai/blob/main/LICENSE
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Default provider, ONLY used when the extraction strategy is LLMExtractionStrategy
DEFAULT_PROVIDER = "openai/gpt-4-turbo"
MODEL_REPO_BRANCH = "new-release-0.0.2"
# Provider-model dictionary, ONLY used when the extraction strategy is LLMExtractionStrategy
PROVIDER_MODELS = {
    "ollama/llama3": "no-token-needed",  # Any model from Ollama no need for API token
    "groq/llama3-70b-8192": os.getenv("GROQ_API_KEY"),
    "groq/llama3-8b-8192": os.getenv("GROQ_API_KEY"),
    "openai/gpt-3.5-turbo": os.getenv("OPENAI_API_KEY"),
    "openai/gpt-4-turbo": os.getenv("OPENAI_API_KEY"),
    "openai/gpt-4o": os.getenv("OPENAI_API_KEY"),
    "anthropic/claude-3-haiku-20240307": os.getenv("ANTHROPIC_API_KEY"),
    "anthropic/claude-3-opus-20240229": os.getenv("ANTHROPIC_API_KEY"),
    "anthropic/claude-3-sonnet-20240229": os.getenv("ANTHROPIC_API_KEY"),
}


# Chunk token threshold
CHUNK_TOKEN_THRESHOLD = 1000

# Threshold for the minimum number of word in a HTML tag to be considered
MIN_WORD_THRESHOLD = 5
