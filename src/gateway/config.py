import os

from dotenv import load_dotenv

load_dotenv()


class LLMGatewayConfig:
    """Central configuration for the LLM gateway."""

    PRIMARY_MODEL = os.getenv(
        "PRIMARY_LLM_MODEL",
        "groq/openai/gpt-oss-20b",
    )

    FALLBACK_MODEL = os.getenv(
        "FALLBACK_LLM_MODEL",
        "gemini/gemini-3.7-flash",
    )

    ROUTING_STRATEGY = os.getenv(
        "LLM_ROUTING_STRATEGY",
        "simple-shuffle",
    )

    NUM_RETRIES = int(
        os.getenv(
            "LLM_NUM_RETRIES",
            "2",
        )
    )

    TIMEOUT = float(
        os.getenv(
            "LLM_TIMEOUT",
            "60",
        )
    )

    CACHE_ENABLED = (
        os.getenv(
            "LLM_CACHE_ENABLED",
            "true",
        ).lower()
        == "true"
    )

    CACHE_TTL = int(
        os.getenv(
            "LLM_CACHE_TTL",
            "3600",
        )
    )

    @classmethod
    def validate(cls):
        """Validate required provider credentials."""

        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )