import logging
import os
from pathlib import Path
from time import perf_counter

import httpx
from dotenv import load_dotenv
from nemoguardrails import LLMRails, RailsConfig

from src.utils.loggers import (
    get_logger,
    log_event,
)

# ============================================================
# LOGGER
# ============================================================

logger = get_logger(__name__)


# ============================================================
# ENVIRONMENT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    PROJECT_ROOT / ".env"
)

NVIDIA_API_KEY = os.getenv(
    "NVIDIA_API_KEY"
)

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


log_event(
    logger,
    level=logging.INFO,
    event="guardrails_initialized",
)


# ============================================================
# INPUT GUARDRAIL
# ============================================================

async def check_input(
    text: str,
) -> bool:
    """
    Validate user input using NeMo Guardrails.

    Returns:
        True  -> input is allowed
        False -> input is blocked or guardrail failed
    """

    if not text or not text.strip():

        log_event(
            logger,
            level=logging.WARNING,
            event="input_guardrail_rejected",
            reason="empty_input",
        )

        return False

    started = perf_counter()

    log_event(
        logger,
        level=logging.INFO,
        event="input_guardrail_started",
    )

    try:

        result = await rails.generate_async(
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ]
        )

        # ----------------------------------------------------
        # CHECK GUARDRAIL RESPONSE
        # ----------------------------------------------------

        if (
           isinstance(result, dict)
           and result.get("role") == "exception"
        ):
            latency_ms = round(
               (
                   perf_counter()
                   - started
               )
               * 1000,
               2,
            )
       
            log_event(
                logger,
                level=logging.WARNING,
                event="input_guardrail_blocked",
                reason="guardrail_exception",
                latency_ms=latency_ms,
            )

            return False

        # ----------------------------------------------------
        # INPUT PASSED
        # ----------------------------------------------------

        latency_ms = round(
            (
                perf_counter()
                - started
            )
            * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            event="input_guardrail_passed",
            latency_ms=latency_ms,
            status="success",
        )

        return True

    except Exception:

        latency_ms = round(
            (
                perf_counter()
                - started
            )
            * 1000,
            2,
        )

        logger.exception(
            "Input guardrail execution failed",
            extra={
                "event": "input_guardrail_failed",
                "context": {
                    "latency_ms": latency_ms,
                },
            },
        )

        # ----------------------------------------------------
        # FAIL CLOSED
        # ----------------------------------------------------

        return False


# ============================================================
# OUTPUT GUARDRAIL
# ============================================================

async def check_output(
    text: str,
) -> bool:
    """
    Validate generated application output.

    Returns:
        True  -> output is safe
        False -> output is unsafe or validation failed
    """

    if not text or not text.strip():

        log_event(
            logger,
            level=logging.WARNING,
            event="output_guardrail_rejected",
            reason="empty_output",
        )

        return False

    started = perf_counter()

    log_event(
        logger,
        level=logging.INFO,
        event="output_guardrail_started",
    )

    try:

        result = await _nvidia_content_safety(
            text
        )

        decision = _extract_safety_decision(
            result
        )

        latency_ms = round(
            (
                perf_counter()
                - started
            )
            * 1000,
            2,
        )

        # ----------------------------------------------------
        # SAFE OUTPUT
        # ----------------------------------------------------

        if decision == "safe":

            log_event(
                logger,
                level=logging.INFO,
                event="output_guardrail_passed",
                decision="safe",
                latency_ms=latency_ms,
                status="success",
            )

            return True

        # ----------------------------------------------------
        # UNSAFE OUTPUT
        # ----------------------------------------------------

        log_event(
            logger,
            level=logging.WARNING,
            event="output_guardrail_blocked",
            decision="unsafe",
            latency_ms=latency_ms,
            status="blocked",
        )

        return False

    except Exception:

        latency_ms = round(
            (
                perf_counter()
                - started
            )
            * 1000,
            2,
        )

        logger.exception(
            "Output guardrail execution failed",
            extra={
                "event": "output_guardrail_failed",
                "context": {
                    "latency_ms": latency_ms,
                },
            },
        )

        # ----------------------------------------------------
        # FAIL CLOSED
        # ----------------------------------------------------

        return False


# ============================================================
# NVIDIA CONTENT SAFETY
# ============================================================

async def _nvidia_content_safety(
    text: str,
):
    """
    Send generated application output to
    NVIDIA Content Safety NIM.

    The generated text itself is intentionally
    not logged.
    """

    url = (
        "https://integrate.api.nvidia.com/v1/chat/completions"
    )

    headers = {
        "Authorization": (
            f"Bearer {NVIDIA_API_KEY}"
        ),
        "Content-Type": "application/json",
    }

    payload = {
        "model": (
            "nvidia/"
            "llama-3.1-nemotron-safety-guard-8b-v3"
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

    request_started = perf_counter()

    log_event(
        logger,
        level=logging.INFO,
        event="nvidia_content_safety_request_started",
    )

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

            response.raise_for_status()

            result = response.json()

        latency_ms = round(
            (
                perf_counter()
                - request_started
            )
            * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            event="nvidia_content_safety_request_completed",
            latency_ms=latency_ms,
            status="success",
        )

        return result

    except Exception:

        latency_ms = round(
            (
                perf_counter()
                - request_started
            )
            * 1000,
            2,
        )

        logger.exception(
            "NVIDIA content safety request failed",
            extra={
                "event": (
                    "nvidia_content_safety_request_failed"
                ),
                "context": {
                    "latency_ms": latency_ms,
                },
            },
        )

        raise


# ============================================================
# SAFETY DECISION EXTRACTION
# ============================================================

def _extract_safety_decision(
    result: dict,
) -> str:
    """
    Extract the safety classification from
    NVIDIA Content Safety response.

    Fail closed if the response is malformed.
    """

    try:

        choices = result.get(
            "choices",
            [],
        )

        if not choices:
            return "unsafe"

        message = choices[0].get(
            "message",
            {},
        )

        content = message.get(
            "content",
            "",
        )

        if not content:
            return "unsafe"

        content = content.lower().strip()

        if "unsafe" in content:
            return "unsafe"

        if "safe" in content:
            return "safe"

        return "unsafe"

    except Exception:

        logger.exception(
            "Failed to extract safety decision",
            extra={
                "event": "safety_decision_extraction_failed",
            },
        )

        return "unsafe"