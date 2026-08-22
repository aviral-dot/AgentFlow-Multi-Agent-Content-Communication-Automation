from unittest.mock import AsyncMock, patch

import pytest

from src.tools.email_tool import EmailTool


@pytest.mark.asyncio
async def test_email_tool_calls_mcp_send_email():
    tool = EmailTool()

    mock_session = AsyncMock()

    mock_session.initialize = AsyncMock()

    mock_session.call_tool = AsyncMock(
        return_value={
            "success": True
        }
    )

    class FakeSessionContext:
        async def __aenter__(self):
            return mock_session

        async def __aexit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            pass

    class FakeStdioContext:
        async def __aenter__(self):
            return "read", "write"

        async def __aexit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            pass

    with patch(
        "src.tools.email_tool.ClientSession",
        return_value=FakeSessionContext(),
    ):
        with patch(
            "src.tools.email_tool.stdio_client",
            return_value=FakeStdioContext(),
        ):
            result = await tool.send(
                to="test@example.com",
                subject="Test",
                body="Hello",
            )

    mock_session.initialize.assert_awaited_once()

    mock_session.call_tool.assert_awaited_once_with(
        "send_email",
        {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Hello",
        },
    )

    assert result == {
        "success": True
    }


@pytest.mark.asyncio
async def test_email_tool_propagates_mcp_error():
    tool = EmailTool()

    mock_session = AsyncMock()

    mock_session.initialize = AsyncMock()

    mock_session.call_tool = AsyncMock(
        side_effect=RuntimeError(
            "MCP server unavailable"
        )
    )

    class FakeSessionContext:
        async def __aenter__(self):
            return mock_session

        async def __aexit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            pass

    class FakeStdioContext:
        async def __aenter__(self):
            return "read", "write"

        async def __aexit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            pass

    with patch(
        "src.tools.email_tool.ClientSession",
        return_value=FakeSessionContext(),
    ):
        with patch(
            "src.tools.email_tool.stdio_client",
            return_value=FakeStdioContext(),
        ):
            with pytest.raises(
                RuntimeError,
                match="MCP server unavailable",
            ):
                await tool.send(
                    to="test@example.com",
                    subject="Test",
                    body="Hello",
                )

    mock_session.initialize.assert_awaited_once()

    mock_session.call_tool.assert_awaited_once()