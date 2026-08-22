from unittest.mock import AsyncMock, patch

import pytest

from src.nodes.mail_node import (
    EmailDraft,
    EmailNode,
)


def test_email_draft_validates_email_structure():
    draft = EmailDraft(
        to="test@example.com",
        subject="Meeting",
        body="See you tomorrow.",
    )

    assert draft.to == "test@example.com"
    assert draft.subject == "Meeting"
    assert draft.body == "See you tomorrow."


@pytest.mark.asyncio
async def test_email_draft_returns_structured_email():
    class FakeStructuredLLM:

        async def ainvoke(self, prompt):
            return EmailDraft(
                to="test@example.com",
                subject="Meeting",
                body="See you tomorrow.",
            )

    class FakeLLM:

        def with_structured_output(self, schema, **kwargs):
            return FakeStructuredLLM()

    node = EmailNode(FakeLLM())

    state = {
        "query": "Send an email to test@example.com about tomorrow's meeting."
    }

    result = await node.draft_email(state)

    assert result["email"]["to"] == "test@example.com"
    assert result["email"]["subject"] == "Meeting"
    assert result["email"]["body"] == "See you tomorrow."


@pytest.mark.asyncio
async def test_send_email_calls_email_tool(sample_email):
    node = object.__new__(EmailNode)

    node.email_tool = AsyncMock()

    node.email_tool.send.return_value = {
        "success": True
    }

    state = {
        "email": sample_email
    }

    result = await node.send_email(state)

    node.email_tool.send.assert_awaited_once_with(
        to="test@example.com",
        subject="Meeting Tomorrow",
        body="This is a test email.",
    )

    assert result["response"] == "Email Sent Successfully"


def test_approve_email_creates_human_approval_interrupt(
    sample_email,
):
    node = object.__new__(EmailNode)

    state = {
        "email": sample_email
    }

    with patch(
        "src.nodes.mail_node.interrupt"
    ) as mock_interrupt:

        mock_interrupt.return_value = "approve"

        result = node.approve_email(state)

    mock_interrupt.assert_called_once()

    payload = mock_interrupt.call_args.args[0]

    assert payload["type"] == "email_approval"
    assert payload["email"]["to"] == "test@example.com"
    assert result["approval"] == "approve"