import logging
from time import perf_counter

from src.states.blogstate import AgentState
from src.utils.loggers import (
    get_logger,
    log_event,
)

logger = get_logger(__name__)


class BlogNode:
    """
    Node responsible for generating blog titles and content.
    """

    def __init__(self, llm):

        self.llm = llm

        log_event(
            logger,
            level=logging.INFO,
            event="blog_node_initialized",
        )

    async def title_creation(
        self,
        state: AgentState,
    ):
        """
        Generate a title for the blog.
        """

        if "query" not in state or not state["query"]:
            log_event(
                logger,
                level=logging.WARNING,
                event="blog_title_generation_skipped",
                reason="query_missing",
            )

            return {}

        prompt = """
You are an expert blog content writer. Use Markdown formatting.
Generate a blog title for the {query}.
This title should be creative and SEO friendly.
"""

        system_message = prompt.format(
            query=state["query"]
        )

        # ----------------------------------------------------
        # TITLE GENERATION
        # ----------------------------------------------------

        generation_started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            event="blog_title_generation_started",
        )

        try:

            response = await self.llm.ainvoke(
                system_message
            )

        except Exception:

            latency_ms = round(
                (perf_counter() - generation_started) * 1000,
                2,
            )

            logger.exception(
                "Blog title generation failed",
                extra={
                    "event": "blog_title_generation_failed",
                    "context": {
                        "latency_ms": latency_ms,
                    },
                },
            )

            raise

        # ----------------------------------------------------
        # TITLE GENERATION COMPLETED
        # ----------------------------------------------------

        latency_ms = round(
            (perf_counter() - generation_started) * 1000,
            2,
        )

        title = response.content

        log_event(
            logger,
            level=logging.INFO,
            event="blog_title_generation_completed",
            latency_ms=latency_ms,
            status="success",
        )

        return {
            "blog": {
                "title": title
            }
        }

    async def content_generation(
        self,
        state: AgentState,
    ):
        """
        Generate the main blog content.
        """

        if "query" not in state or not state["query"]:
            log_event(
                logger,
                level=logging.WARNING,
                event="blog_content_generation_skipped",
                reason="query_missing",
            )

            return {}

        system_prompt = """
You are an expert blog writer. Use Markdown formatting.
Generate detailed blog content with a detailed breakdown
for the {query}.
"""

        system_message = system_prompt.format(
            query=state["query"]
        )

        # ----------------------------------------------------
        # CONTENT GENERATION
        # ----------------------------------------------------

        generation_started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            event="blog_content_generation_started",
        )

        try:

            response = await self.llm.ainvoke(
                system_message
            )

        except Exception:

            latency_ms = round(
                (perf_counter() - generation_started) * 1000,
                2,
            )

            logger.exception(
                "Blog content generation failed",
                extra={
                    "event": "blog_content_generation_failed",
                    "context": {
                        "latency_ms": latency_ms,
                    },
                },
            )

            raise

        # ----------------------------------------------------
        # CONTENT GENERATION COMPLETED
        # ----------------------------------------------------

        latency_ms = round(
            (perf_counter() - generation_started) * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            event="blog_content_generation_completed",
            latency_ms=latency_ms,
            status="success",
        )

        return {
            "blog": {
                "title": state["blog"]["title"],
                "content": response.content,
            }
        }