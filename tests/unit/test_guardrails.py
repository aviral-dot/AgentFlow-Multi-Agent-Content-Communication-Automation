from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.guardrails.guardrail import (
    check_input,
    check_output,
    _extract_safety_decision,
    _nvidia_content_safety,
)


# ============================================================
# check_input()
# ============================================================


@pytest.mark.asyncio
async def test_empty_input_is_rejected():
    result = await check_input("")

    assert result is False


@pytest.mark.asyncio
async def test_whitespace_input_is_rejected():
    result = await check_input("   ")

    assert result is False


@pytest.mark.asyncio
async def test_safe_input_is_allowed():
    mock_result = {
        "role": "assistant",
        "content": "safe",
    }

    with patch(
        "src.guardrails.guardrail.rails.generate_async",
        new=AsyncMock(return_value=mock_result),
    ) as mock_generate:

        result = await check_input(
            "Write a blog about artificial intelligence."
        )

    assert result is True
    mock_generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_input_with_exception_role_is_rejected():
    mock_result = {
        "role": "exception",
        "content": "Input blocked by guardrail",
    }

    with patch(
        "src.guardrails.guardrail.rails.generate_async",
        new=AsyncMock(return_value=mock_result),
    ):

        result = await check_input(
            "Generate harmful content."
        )

    assert result is False


@pytest.mark.asyncio
async def test_input_with_non_exception_role_is_allowed():
    mock_result = {
        "role": "assistant",
        "content": "Anything else",
    }

    with patch(
        "src.guardrails.guardrail.rails.generate_async",
        new=AsyncMock(return_value=mock_result),
    ):

        result = await check_input(
            "Write a blog about Python."
        )

    assert result is True


@pytest.mark.asyncio
async def test_input_with_non_dict_result_is_allowed():
    mock_result = "safe response"

    with patch(
        "src.guardrails.guardrail.rails.generate_async",
        new=AsyncMock(return_value=mock_result),
    ):

        result = await check_input(
            "Write a blog about AI."
        )

    assert result is True


@pytest.mark.asyncio
async def test_guardrail_exception_fails_closed():
    with patch(
        "src.guardrails.guardrail.rails.generate_async",
        new=AsyncMock(
            side_effect=RuntimeError(
                "Guardrail unavailable"
            )
        ),
    ):

        result = await check_input(
            "Write a blog about AI."
        )

    assert result is False


# ============================================================
# check_output()
# ============================================================


@pytest.mark.asyncio
async def test_empty_output_is_rejected():
    result = await check_output("")

    assert result is False


@pytest.mark.asyncio
async def test_whitespace_output_is_rejected():
    result = await check_output("   ")

    assert result is False


@pytest.mark.asyncio
async def test_safe_output_is_allowed():
    mock_result = {
        "choices": [
            {
                "message": {
                    "content": "safe"
                }
            }
        ]
    }

    with patch(
        "src.guardrails.guardrail._nvidia_content_safety",
        new=AsyncMock(return_value=mock_result),
    ) as mock_safety:

        result = await check_output(
            "This is safe generated content."
        )

    assert result is True
    mock_safety.assert_awaited_once_with(
        "This is safe generated content."
    )


@pytest.mark.asyncio
async def test_unsafe_output_is_rejected():
    mock_result = {
        "choices": [
            {
                "message": {
                    "content": "unsafe"
                }
            }
        ]
    }

    with patch(
        "src.guardrails.guardrail._nvidia_content_safety",
        new=AsyncMock(return_value=mock_result),
    ):

        result = await check_output(
            "Unsafe generated content."
        )

    assert result is False


@pytest.mark.asyncio
async def test_unknown_output_decision_fails_closed():
    mock_result = {
        "choices": [
            {
                "message": {
                    "content": "unknown"
                }
            }
        ]
    }

    with patch(
        "src.guardrails.guardrail._nvidia_content_safety",
        new=AsyncMock(return_value=mock_result),
    ):

        result = await check_output(
            "Generated content."
        )

    assert result is False


@pytest.mark.asyncio
async def test_malformed_output_response_fails_closed():
    mock_result = {}

    with patch(
        "src.guardrails.guardrail._nvidia_content_safety",
        new=AsyncMock(return_value=mock_result),
    ):

        result = await check_output(
            "Generated content."
        )

    assert result is False


@pytest.mark.asyncio
async def test_output_guardrail_fails_closed_on_api_error():
    with patch(
        "src.guardrails.guardrail._nvidia_content_safety",
        new=AsyncMock(
            side_effect=RuntimeError(
                "NVIDIA unavailable"
            )
        ),
    ):

        result = await check_output(
            "Safe generated content"
        )

    assert result is False


# ============================================================
# _extract_safety_decision()
# ============================================================


def test_extract_safe_decision():
    result = {
        "choices": [
            {
                "message": {
                    "content": "safe"
                }
            }
        ]
    }

    assert _extract_safety_decision(result) == "safe"


def test_extract_unsafe_decision():
    result = {
        "choices": [
            {
                "message": {
                    "content": "unsafe"
                }
            }
        ]
    }

    assert _extract_safety_decision(result) == "unsafe"


def test_extract_safe_decision_is_case_insensitive():
    result = {
        "choices": [
            {
                "message": {
                    "content": "SAFE"
                }
            }
        ]
    }

    assert _extract_safety_decision(result) == "safe"


def test_extract_decision_strips_whitespace():
    result = {
        "choices": [
            {
                "message": {
                    "content": "  safe  "
                }
            }
        ]
    }

    assert _extract_safety_decision(result) == "safe"


def test_missing_safety_response_is_unsafe():
    result = {}

    assert _extract_safety_decision(result) == "unsafe"


def test_empty_choices_is_unsafe():
    result = {
        "choices": []
    }

    assert _extract_safety_decision(result) == "unsafe"


def test_missing_message_is_unsafe():
    result = {
        "choices": [
            {}
        ]
    }

    assert _extract_safety_decision(result) == "unsafe"


def test_missing_content_is_unsafe():
    result = {
        "choices": [
            {
                "message": {}
            }
        ]
    }

    assert _extract_safety_decision(result) == "unsafe"


def test_empty_content_is_unsafe():
    result = {
        "choices": [
            {
                "message": {
                    "content": ""
                }
            }
        ]
    }

    assert _extract_safety_decision(result) == "unsafe"


def test_none_content_is_unsafe():
    result = {
        "choices": [
            {
                "message": {
                    "content": None
                }
            }
        ]
    }

    assert _extract_safety_decision(result) == "unsafe"


def test_unknown_decision_is_unsafe():
    result = {
        "choices": [
            {
                "message": {
                    "content": "maybe"
                }
            }
        ]
    }

    assert _extract_safety_decision(result) == "unsafe"


def test_unsafe_is_checked_before_safe():
    result = {
        "choices": [
            {
                "message": {
                    "content": "unsafe"
                }
            }
        ]
    }

    assert _extract_safety_decision(result) == "unsafe"


def test_extract_malformed_choices_is_unsafe():
    result = {
        "choices": None
    }

    assert _extract_safety_decision(result) == "unsafe"


def test_extract_invalid_result_type_is_unsafe():
    result = None

    assert _extract_safety_decision(result) == "unsafe"


# ============================================================
# _nvidia_content_safety()
# ============================================================


@pytest.mark.asyncio
async def test_nvidia_content_safety_success():
    mock_response = MagicMock()

    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "safe"
                }
            }
        ]
    }

    mock_response.raise_for_status.return_value = None

    with patch(
        "src.guardrails.guardrail.httpx.AsyncClient"
    ) as mock_client:

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response

        mock_client.return_value.__aenter__.return_value = (
            mock_client_instance
        )

        result = await _nvidia_content_safety(
            "Safe content"
        )

    assert result == {
        "choices": [
            {
                "message": {
                    "content": "safe"
                }
            }
        ]
    }

    mock_client_instance.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_nvidia_content_safety_sends_expected_request():
    mock_response = MagicMock()

    mock_response.json.return_value = {
        "choices": []
    }

    mock_response.raise_for_status.return_value = None

    with patch(
        "src.guardrails.guardrail.httpx.AsyncClient"
    ) as mock_client:

        mock_client_instance = AsyncMock()

        mock_client_instance.post.return_value = mock_response

        mock_client.return_value.__aenter__.return_value = (
            mock_client_instance
        )

        await _nvidia_content_safety(
            "Test content"
        )

    mock_client_instance.post.assert_awaited_once()

    call_args = mock_client_instance.post.call_args

    # URL is passed positionally in the implementation.
    assert (
        call_args.args[0]
        == "https://integrate.api.nvidia.com/v1/chat/completions"
    )

    call_kwargs = call_args.kwargs

    assert (
        call_kwargs["json"]["model"]
        == "nvidia/llama-3.1-nemotron-safety-guard-8b-v3"
    )

    assert (
        call_kwargs["json"]["messages"][0]["role"]
        == "user"
    )

    assert (
        call_kwargs["json"]["messages"][0]["content"]
        == "Test content"
    )

    assert call_kwargs["json"]["temperature"] == 0.0
    assert call_kwargs["json"]["max_tokens"] == 100


@pytest.mark.asyncio
async def test_nvidia_content_safety_raises_on_http_error():
    mock_response = MagicMock()

    mock_response.raise_for_status.side_effect = (
        httpx.HTTPStatusError(
            "Unauthorized",
            request=MagicMock(),
            response=MagicMock(),
        )
    )

    with patch(
        "src.guardrails.guardrail.httpx.AsyncClient"
    ) as mock_client:

        mock_client_instance = AsyncMock()

        mock_client_instance.post.return_value = mock_response

        mock_client.return_value.__aenter__.return_value = (
            mock_client_instance
        )

        with pytest.raises(httpx.HTTPStatusError):
            await _nvidia_content_safety(
                "Test content"
            )