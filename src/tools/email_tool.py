import logging
import sys
from pathlib import Path
from time import perf_counter

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from src.utils.loggers import (
    get_logger,
    log_event,
)

logger = get_logger(__name__)


class EmailTool:

    def __init__(self):

        base_dir = Path(__file__).resolve().parents[2]

        self.server = StdioServerParameters(
            command=str(
                Path(sys.executable).resolve()
            ),
            args=[
                str(
                    base_dir / "gmail_mcp_server.py"
                )
            ],
        )

        log_event(
            logger,
            level=logging.INFO,
            event="email_tool_initialized",
        )

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
    ):
        """
        Send an email through the Gmail MCP server.

        Sensitive email data is intentionally not logged.
        """

        send_started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            event="email_tool_send_started",
        )

        try:

            # ------------------------------------------------
            # START MCP CLIENT
            # ------------------------------------------------

            log_event(
                logger,
                level=logging.INFO,
                event="gmail_mcp_connection_started",
            )

            async with (
                     stdio_client(self.server) as (read, write),
                     ClientSession(read, write) as session,
                ):

                    # ----------------------------------------
                    # INITIALIZE MCP SESSION
                    # ----------------------------------------

                    await session.initialize()

                    log_event(
                        logger,
                        level=logging.INFO,
                        event="gmail_mcp_connection_initialized",
                    )

                    # ----------------------------------------
                    # CALL SEND EMAIL TOOL
                    # ----------------------------------------

                    tool_started = perf_counter()

                    log_event(
                        logger,
                        level=logging.INFO,
                        event="gmail_send_tool_call_started",
                    )

                    result = await session.call_tool(
                        "send_email",
                        {
                            "to": to,
                            "subject": subject,
                            "body": body,
                        },
                    )

                    tool_latency_ms = round(
                        (
                            perf_counter()
                            - tool_started
                        )
                        * 1000,
                        2,
                    )

                    log_event(
                        logger,
                        level=logging.INFO,
                        event="gmail_send_tool_call_completed",
                        latency_ms=tool_latency_ms,
                        status="success",
                    )

                    # ----------------------------------------
                    # SEND COMPLETED
                    # ----------------------------------------

                    total_latency_ms = round(
                        (
                            perf_counter()
                            - send_started
                        )
                        * 1000,
                        2,
                    )

                    log_event(
                        logger,
                        level=logging.INFO,
                        event="email_tool_send_completed",
                        latency_ms=total_latency_ms,
                        status="success",
                    )

                    return result

        except Exception:

            total_latency_ms = round(
                (
                    perf_counter()
                    - send_started
                )
                * 1000,
                2,
            )

            logger.exception(
                "Email tool send failed",
                extra={
                    "event": "email_tool_send_failed",
                    "context": {
                        "latency_ms": total_latency_ms,
                    },
                },
            )

            raise