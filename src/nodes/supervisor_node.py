from typing import Literal

from pydantic import BaseModel, Field

from src.states.blogstate import AgentState


class SupervisorDecision(BaseModel):

    route: Literal["blog", "email"] = Field(
        description=(
            "Routing decision. "
            "Must be exactly lowercase "
            "'blog' or 'email'."
        )
    )


class SupervisorNode:

    def __init__(self, llm):

        self.llm = llm

        self.structured_llm = llm.with_structured_output(
            SupervisorDecision
        )

    def decide(self, state: AgentState):

        query = state["query"]

        prompt = f"""
You are a supervisor for a multi-agent system.

Available agents:

BLOG
- Handles blog/content generation requests.

EMAIL
- Handles sending email requests.

Choose exactly ONE agent.

User Query:
{query}

Rules:

- If the user wants to send, compose, draft, or handle an email,
  choose EMAIL.
- If the user wants to create, write, or generate a blog,
  choose BLOG.
"""

        decision = self.structured_llm.invoke(prompt)

        return {
            "route": decision.route
        }