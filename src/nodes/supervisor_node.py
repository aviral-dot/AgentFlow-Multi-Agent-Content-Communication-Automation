import logging
from time import perf_counter
from typing import Literal

from pydantic import BaseModel, Field

from src.states.blogstate import AgentState
from src.utils.loggers import get_logger, log_event

logger = get_logger(__name__)

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

        log_event(
            logger,
            level=logging.INFO,
            event="supervisor_initialized",
        )

    async def decide(self, state: AgentState):

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

        routing_started = perf_counter()

        log_event(
            logger,
            level = logging.INFO,
            event = "supervisor routing started"
        )

        try:

            decision = await self.structured_llm.ainvoke(
                prompt
            )

        except Exception:

            latency_ms = round(
                (perf_counter() - routing_started) * 1000,
                2,
            )

            logger.exception(
                "Supervisor routing failed",
                extra={
                    "event": "supervisor_routing_failed",
                    "context": {
                        "latency_ms": latency_ms,
                    },
                },
            )

            raise

        # ----------------------------------------------------
        # ROUTING COMPLETED
        # ----------------------------------------------------

        latency_ms = round(
            (perf_counter() - routing_started) * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            event="supervisor_routing_completed",
            route=decision.route,
            latency_ms=latency_ms,
            status="success",
        )

        return {
            "route": decision.route
        }