from pathlib import Path
import os
import json

import httpx
from dotenv import load_dotenv
from nemoguardrails import RailsConfig, LLMRails


# ============================================================
# ENVIRONMENT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")


if not NVIDIA_API_KEY:
    raise RuntimeError(
        "NVIDIA_API_KEY is missing from .env"
    )


# ============================================================
# GUARDRAIL CONFIGURATION
# ============================================================

GUARDRAIL_DIR = Path(__file__).resolve().parent

config = RailsConfig.from_path(
    str(GUARDRAIL_DIR)
)

rails = LLMRails(config)


# ============================================================
# INPUT SECURITY
# ============================================================

async def check_input(text: str) -> bool:

    if not text or not text.strip():
        return False

    try:

        result = await rails.generate_async(
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ]
        )

        print(
            "\n========== INPUT GUARDRAIL =========="
        )

        print(result)

        # ----------------------------------------------------
        # NeMo rail blocked the request
        # ----------------------------------------------------

        if isinstance(result, dict):

            if result.get("role") == "exception":

                print(
                    "🚫 INPUT BLOCKED BY GUARDRAIL"
                )

                return False

        print(
            "✅ INPUT PASSED SECURITY"
        )

        return True

    except Exception as e:

      print("\n" + "=" * 80)
      print("🚨 INPUT GUARDRAIL EXCEPTION")
      print("=" * 80)

      print("TYPE:")
      print(type(e).__name__)

      print("\nMESSAGE:")
      print(str(e))

      print("\nREPR:")
      print(repr(e))

      return False


# ============================================================
# OUTPUT SECURITY
#
# This function is for YOUR LangGraph/Groq output.
#
# app.py does NOT need to change.
# ============================================================

async def check_output(text: str) -> bool:

    if not text or not text.strip():
        return False

    try:

        print(
            "\n========== OUTPUT SAFETY =========="
        )

        result = await _nvidia_content_safety(text)

        print(
            "NVIDIA SAFETY RESULT:",
            result
        )

        # ----------------------------------------------------
        # Extract safety decision
        # ----------------------------------------------------

        decision = _extract_safety_decision(result)

        print(
            "OUTPUT DECISION:",
            decision
        )

        if decision == "safe":

            print(
                "✅ OUTPUT PASSED SECURITY"
            )

            return True

        print(
            "🚫 OUTPUT BLOCKED"
        )

        return False

    except Exception as e:

        print(
            "\n🚫 OUTPUT SECURITY ERROR"
        )

        print(
            f"Reason: {e}"
        )

        # Fail closed.
        return False


# ============================================================
# NVIDIA CONTENT SAFETY CALL
# ============================================================

async def _nvidia_content_safety(
    text: str,
):
    """
    Send already-generated LangGraph/Groq output
    to NVIDIA's Content Safety NIM.

    This is separate from NeMo's generation pipeline.
    """

    url = (
        "https://integrate.api.nvidia.com/v1/chat/completions"
    )

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": (
            "nvidia/llama-3.1-nemotron-safety-guard-8b-v3"
        ),
        "messages": [
            {
                "role": "user",
                "content": text,
            }
        ],
        "temperature": 0.0,
        "max_tokens": 100,
    }

    async with httpx.AsyncClient(
        timeout=30.0
    ) as client:

        response = await client.post(
            url,
            headers=headers,
            json=payload,
        )

        response.raise_for_status()

        return response.json()


# ============================================================
# SAFETY DECISION PARSER
# ============================================================

def _extract_safety_decision(
    result: dict,
) -> str:

    try:

        choices = result.get(
            "choices",
            []
        )

        if not choices:
            return "unsafe"

        message = choices[0].get(
            "message",
            {}
        )

        content = message.get(
            "content",
            ""
        )

        if not content:
            return "unsafe"

        content = content.lower().strip()

        print(
            "RAW SAFETY CLASSIFICATION:",
            content
        )

        # ----------------------------------------------------
        # Strong unsafe indicators
        # ----------------------------------------------------

        if "unsafe" in content:

            return "unsafe"

        # ----------------------------------------------------
        # Explicit safe result
        # ----------------------------------------------------

        if "safe" in content:

            return "safe"

        # ----------------------------------------------------
        # Anything unexpected = BLOCK
        # ----------------------------------------------------

        return "unsafe"

    except Exception:

        return "unsafe"