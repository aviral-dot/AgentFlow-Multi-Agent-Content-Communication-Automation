from types import SimpleNamespace

import pytest


class FakeLLM:
    """
    Fake LLM used by tests.

    It never calls a real LLM provider.
    """

    def __init__(self, response="fake response"):
        self.response = response

    async def ainvoke(self, prompt):
        return SimpleNamespace(
            content=self.response
        )

    def with_structured_output(
        self,
        schema,
        **kwargs,
    ):
        return FakeStructuredLLM(schema)


class FakeStructuredLLM:
    """
    Fake structured-output LLM.

    Tests can configure the returned object.
    """

    def __init__(self, schema):
        self.schema = schema
        self.result = None

    async def ainvoke(self, prompt):
        return self.result


@pytest.fixture
def fake_llm():
    return FakeLLM()


@pytest.fixture
def sample_blog_state():
    return {
        "query": (
            "Write a blog about Generative AI"
        ),
    }


@pytest.fixture
def sample_email():
    return {
        "to": "test@example.com",
        "subject": "Meeting Tomorrow",
        "body": "This is a test email.",
    }


@pytest.fixture
def sample_email_state(sample_email):
    return {
        "query": (
            "Send an email to "
            "test@example.com about tomorrow's meeting."
        ),
        "email": sample_email,
    }