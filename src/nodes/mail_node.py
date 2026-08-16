from pydantic import BaseModel
from src.states.blogstate import AgentState
from src.tools.email_tool import EmailTool


class EmailDraft(BaseModel):
    to: str
    subject: str
    body: str


class EmailNode:

    def __init__(self, llm):
        self.llm = llm
        self.email_tool = EmailTool()

        # LLM returns EmailDraft object
        self.structured_llm = llm.with_structured_output(EmailDraft)

    def draft_email(self, state: AgentState):

        query = state["query"]

        prompt = f"""
You are an AI Email Assistant.

The user request is:

{query}

Extract:

1. Recipient Email
2. Subject
3. Email Body

Return only the structured output.
"""

        draft = self.structured_llm.invoke(prompt)

        return {
            "email": {
                "to": draft.to,
                "subject": draft.subject,
                "body": draft.body
            }
        }

    async def send_email(self, state: AgentState):

        email = state["email"]

        result = await self.email_tool.send(
            to=email["to"],
            subject=email["subject"],
            body=email["body"]
        )


        return {
            "response": "Email Sent Successfully",
            "tool_result": result
        }
    