from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
import app


client = TestClient(app.app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Multi-Agent AI System is running"
    }


def test_chat_requires_query():
    response = client.post(
        "/chat",
        json={
            "thread_id": "test-thread",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Query is required"
    )


def test_chat_requires_thread_id():
    response = client.post(
        "/chat",
        json={
            "query": "Write a blog about AI",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "thread_id is required"
    )


def test_chat_rejects_empty_query():
    response = client.post(
        "/chat",
        json={
            "query": "   ",
            "thread_id": "test-thread",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Query is required"
    )


def test_chat_blocks_unsafe_input():
    with patch(
        "app.check_input",
        new=AsyncMock(return_value=False),
    ):
        response = client.post(
            "/chat",
            json={
                "query": "Unsafe request",
                "thread_id": "test-thread",
            },
        )

    assert response.status_code == 200

    assert response.json() == {
        "success": False,
        "blocked": True,
        "stage": "input",
        "reason": (
            "Input blocked by "
            "security guardrail"
        ),
    }


def test_chat_returns_blog_response():
    fake_graph = MagicMock()

    fake_graph.ainvoke = AsyncMock(
        return_value={
            "route": "blog",
            "query": "Write a blog about AI",
            "blog": {
                "title": "The Future of AI",
                "content": (
                    "AI is transforming "
                    "software development."
                ),
            },
        }
    )

    with (
        patch(
            "app.graph",
            fake_graph,
        ),
        patch(
            "app.check_input",
            new=AsyncMock(return_value=True),
        ),
        patch(
            "app.check_output",
            new=AsyncMock(return_value=True),
        ),
    ):
        response = client.post(
            "/chat",
            json={
                "query": "Write a blog about AI",
                "thread_id": "test-thread",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["blocked"] is False
    assert data["status"] == "completed"

    assert data["data"]["route"] == "blog"

    assert data["data"]["thread_id"] == (
        "test-thread"
    )

    assert data["data"]["response"] == (
        "# The Future of AI\n\n"
        "AI is transforming software development."
    )

    fake_graph.ainvoke.assert_awaited_once()


def test_chat_blocks_unsafe_output():
    fake_graph = MagicMock()

    fake_graph.ainvoke = AsyncMock(
        return_value={
            "route": "blog",
            "query": "Write a blog about AI",
            "blog": {
                "title": "The Future of AI",
                "content": "Generated content",
            },
        }
    )

    with (
        patch(
            "app.graph",
            fake_graph,
        ),
        patch(
            "app.check_input",
            new=AsyncMock(return_value=True),
        ),
        patch(
            "app.check_output",
            new=AsyncMock(return_value=False),
        ),
    ):
        response = client.post(
            "/chat",
            json={
                "query": "Write a blog about AI",
                "thread_id": "test-thread",
            },
        )

    assert response.status_code == 200

    assert response.json() == {
        "success": False,
        "blocked": True,
        "stage": "output",
        "reason": (
            "Generated response blocked "
            "by security guardrail"
        ),
    }


def test_chat_returns_approval_required():
    fake_graph = MagicMock()

    fake_graph.ainvoke = AsyncMock(
        return_value={
            "__interrupt__": [
                MagicMock(
                    value={
                        "type": "email_approval",
                        "email": {
                            "to": "test@example.com",
                            "subject": "Test",
                            "body": "Hello",
                        },
                    }
                )
            ]
        }
    )

    with (
        patch(
            "app.graph",
            fake_graph,
        ),
        patch(
            "app.check_input",
            new=AsyncMock(return_value=True),
        ),
    ):
        response = client.post(
            "/chat",
            json={
                "query": (
                    "Send an email to "
                    "test@example.com"
                ),
                "thread_id": "email-thread",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["blocked"] is False
    assert data["status"] == (
        "approval_required"
    )
    assert data["thread_id"] == (
        "email-thread"
    )

    assert data["approval"]["type"] == (
        "email_approval"
    )


def test_chat_returns_500_when_graph_fails():
    fake_graph = MagicMock()

    fake_graph.ainvoke = AsyncMock(
        side_effect=RuntimeError(
            "Database unavailable"
        )
    )

    with (
        patch(
            "app.graph",
            fake_graph,
        ),
        patch(
            "app.check_input",
            new=AsyncMock(return_value=True),
        ),
    ):
        response = client.post(
            "/chat",
            json={
                "query": "Write a blog about AI",
                "thread_id": "test-thread",
            },
        )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Internal server error"
    }


def test_email_approval_requires_thread_id():
    response = client.post(
        "/email/approval",
        json={
            "decision": "approve",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "thread_id is required"
    )


def test_email_approval_rejects_invalid_decision():
    response = client.post(
        "/email/approval",
        json={
            "thread_id": "email-thread",
            "decision": "maybe",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "decision must be "
        "'approve' or 'reject'"
    )


def test_email_approval_rejects_email():
    fake_graph = MagicMock()

    fake_graph.ainvoke = AsyncMock(
        return_value={
            "route": "email",
            "response": "Email rejected.",
        }
    )

    with patch(
        "app.graph",
        fake_graph,
    ):
        response = client.post(
            "/email/approval",
            json={
                "thread_id": "email-thread",
                "decision": "reject",
            },
        )

    assert response.status_code == 200

    assert response.json() == {
        "success": True,
        "blocked": False,
        "status": "rejected",
        "thread_id": "email-thread",
        "message": (
            "Email rejected. "
            "Nothing was sent."
        ),
    }


def test_email_approval_sends_email_after_approval():
    fake_graph = MagicMock()

    fake_graph.ainvoke = AsyncMock(
        return_value={
            "route": "email",
            "response": "Email sent successfully.",
        }
    )

    with (
        patch(
            "app.graph",
            fake_graph,
        ),
        patch(
            "app.check_output",
            new=AsyncMock(return_value=True),
        ),
    ):
        response = client.post(
            "/email/approval",
            json={
                "thread_id": "email-thread",
                "decision": "approve",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["blocked"] is False
    assert data["status"] == "completed"
    assert data["thread_id"] == (
        "email-thread"
    )

    assert data["data"]["route"] == "email"

    assert data["data"]["response"] == (
        "Email sent successfully."
    )


def test_email_approval_blocks_unsafe_output():
    fake_graph = MagicMock()

    fake_graph.ainvoke = AsyncMock(
        return_value={
            "route": "email",
            "response": "Email sent successfully.",
        }
    )

    with (
        patch(
            "app.graph",
            fake_graph,
        ),
        patch(
            "app.check_output",
            new=AsyncMock(return_value=False),
        ),
    ):
        response = client.post(
            "/email/approval",
            json={
                "thread_id": "email-thread",
                "decision": "approve",
            },
        )

    assert response.status_code == 200

    assert response.json() == {
        "success": False,
        "blocked": True,
        "stage": "output",
        "thread_id": "email-thread",
        "reason": (
            "Generated response blocked "
            "by security guardrail"
        ),
    }