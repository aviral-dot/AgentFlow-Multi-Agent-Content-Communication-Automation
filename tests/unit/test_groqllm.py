from unittest.mock import MagicMock, patch

import pytest

from src.llms.groqllm import GroqLLM


def test_groq_llm_loads_environment():
    with patch(
        "src.llms.groqllm.load_dotenv"
    ) as mock_load_dotenv:

        GroqLLM()

    mock_load_dotenv.assert_called_once()


@patch("src.llms.groqllm.ChatGroq")
@patch("src.llms.groqllm.os.getenv")
def test_get_llm_returns_chatgroq(
    mock_getenv,
    mock_chatgroq,
):
    mock_getenv.return_value = "test-groq-api-key"

    mock_llm = MagicMock()
    mock_chatgroq.return_value = mock_llm

    groq = GroqLLM()

    result = groq.get_llm()

    assert result is mock_llm

    mock_chatgroq.assert_called_once_with(
        api_key="test-groq-api-key",
        model="openai/gpt-oss-20b",
    )


@patch("src.llms.groqllm.ChatGroq")
@patch("src.llms.groqllm.os.getenv")
def test_get_llm_stores_api_key(
    mock_getenv,
    mock_chatgroq,
):
    mock_getenv.return_value = "test-groq-api-key"

    groq = GroqLLM()

    groq.get_llm()

    assert (
        groq.groq_api_key
        == "test-groq-api-key"
    )


@patch("src.llms.groqllm.ChatGroq")
@patch("src.llms.groqllm.os.getenv")
def test_get_llm_fails_when_api_key_missing(
    mock_getenv,
    mock_chatgroq,
):
    mock_getenv.return_value = None

    groq = GroqLLM()

    with pytest.raises(
        ValueError,
        match="GROQ_API_KEY is not configured",
    ):
        groq.get_llm()

    mock_chatgroq.assert_not_called()


@patch("src.llms.groqllm.ChatGroq")
@patch("src.llms.groqllm.os.getenv")
def test_get_llm_wraps_chatgroq_exception(
    mock_getenv,
    mock_chatgroq,
):
    mock_getenv.return_value = "test-groq-api-key"

    mock_chatgroq.side_effect = RuntimeError(
        "Groq initialization failed"
    )

    groq = GroqLLM()

    with pytest.raises(
        ValueError,
        match="Failed to initialize Groq LLM",
    ):
        groq.get_llm()