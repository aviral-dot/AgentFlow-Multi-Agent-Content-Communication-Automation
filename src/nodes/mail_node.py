# from pydantic import BaseModel
# from src.states.blogstate import AgentState
# from src.tools.email_tool import EmailTool


# class EmailDraft(BaseModel):
#     to: str
#     subject: str
#     body: str


# class EmailNode:

#     def __init__(self, llm):
#         self.llm = llm
#         self.email_tool = EmailTool()

#         # LLM returns EmailDraft object
#         self.structured_llm = llm.with_structured_output(EmailDraft)

#     def draft_email(self, state: AgentState):

#         query = state["query"]

#         prompt = f"""
# You are an AI Email Assistant.

# The user request is:

# {query}

# Extract:

# 1. Recipient Email
# 2. Subject
# 3. Email Body

# Return only the structured output.
# """

#         draft = self.structured_llm.invoke(prompt)

#         return {
#             "email": {
#                 "to": draft.to,
#                 "subject": draft.subject,
#                 "body": draft.body
#             }
#         }

#     async def send_email(self, state: AgentState):

#         email = state["email"]

#         result = await self.email_tool.send(
#             to=email["to"],
#             subject=email["subject"],
#             body=email["body"]
#         )


#         return {
#             "response": "Email Sent Successfully",
#             "tool_result": result
#         }
    


from pydantic import BaseModel

from langgraph.types import interrupt

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

        self.structured_llm = llm.with_structured_output(
            EmailDraft,
            method="json_mode"
        )

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

Return ONLY valid JSON with exactly these fields:

{{
    "to": "recipient@example.com",
    "subject": "Email subject",
    "body": "Email body"
}}

Do not return markdown.
Do not return explanations.
Do not return any text outside the JSON.
"""

        draft = self.structured_llm.invoke(prompt)

        return {
            "email": {
                "to": draft.to,
                "subject": draft.subject,
                "body": draft.body
            }
        }

    def approve_email(self, state: AgentState):

        email = state["email"]

        decision = interrupt(
            {
                "type": "email_approval",
                "message": "Please approve or reject this email before sending.",
                "email": {
                    "to": email["to"],
                    "subject": email["subject"],
                    "body": email["body"]
                }
            }
        )

        return {
            "approval": decision
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
    