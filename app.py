import asyncio
import logging
import os
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from src.gateway.llm_gateway import LLMGateway
from src.graphs.graph_builder import GraphBuilder
from src.guardrails.guardrail import (
    check_input,
    check_output,
)
from src.utils.loggers import (
    get_logger,
    log_event,
)

# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# LOGGER
# ============================================================

logger = get_logger(__name__)


# ============================================================
# LLM INITIALIZATION
# ============================================================

llm_gateway = LLMGateway()

log_event(
    logger,
    level=logging.INFO,
    event="llm_gateway_initialized",
)

llm = llm_gateway.get_llm(
    model_name="primary",
    temperature=0.2,
)

log_event(
    logger,
    level=logging.INFO,
    event="primary_llm_initialized",
)


# ============================================================
# GLOBAL GRAPH / CHECKPOINTER
# ============================================================

graph = None
checkpointer = None


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    global graph
    global checkpointer

    database_url = os.getenv(
        "DATABASE_URL"
    )

    if not database_url:

        log_event(
            logger,
            level=logging.ERROR,
            event="application_startup_failed",
            reason="database_url_not_configured",
        )

        raise RuntimeError(
            "DATABASE_URL environment variable "
            "is not configured."
        )

    log_event(
        logger,
        level=logging.INFO,
        event="application_startup_started",
    )

    try:

        log_event(
            logger,
            level=logging.INFO,
            event="postgres_checkpointer_initialization_started",
        )

        async with AsyncPostgresSaver.from_conn_string(
            database_url
        ) as saver:

            await saver.setup()

            log_event(
                logger,
                level=logging.INFO,
                event="postgres_checkpointer_initialized",
                status="success",
            )

            checkpointer = saver

            graph_builder = GraphBuilder(
                llm,
                checkpointer,
            )

            graph = graph_builder.setup_graph()

            log_event(
                logger,
                level=logging.INFO,
                event="langgraph_initialized",
                persistence="postgresql",
                status="success",
            )

            log_event(
                logger,
                level=logging.INFO,
                event="application_startup_completed",
                status="success",
            )

            yield

    except Exception:

        logger.exception(
            "Application startup failed",
            extra={
                "event": "application_startup_failed",
                "context": {},
            },
        )

        raise

    finally:

        graph = None
        checkpointer = None

        log_event(
            logger,
            level=logging.INFO,
            event="postgres_checkpointer_closed",
        )

        log_event(
            logger,
            level=logging.INFO,
            event="application_shutdown_completed",
        )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Blog and Email Multi-Agent API",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():

    return {
        "message": "Multi-Agent AI System is running"
    }


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post("/chat")
async def chat(request: Request):

    request_id = str(uuid4())
    request_started = perf_counter()

    thread_id = None

    log_event(
        logger,
        level=logging.INFO,
        event="chat_request_started",
        request_id=request_id,
    )

    try:

        # ----------------------------------------------------
        # PARSE REQUEST
        # ----------------------------------------------------

        data = await request.json()

        query = data.get(
            "query",
            "",
        ).strip()

        thread_id = data.get(
            "thread_id"
        )

        # ----------------------------------------------------
        # VALIDATE REQUEST
        # ----------------------------------------------------

        if not query:

            log_event(
                logger,
                level=logging.WARNING,
                event="chat_request_validation_failed",
                request_id=request_id,
                reason="query_missing",
            )

            raise HTTPException(
                status_code=400,
                detail="Query is required",
            )

        if not thread_id:

            log_event(
                logger,
                level=logging.WARNING,
                event="chat_request_validation_failed",
                request_id=request_id,
                reason="thread_id_missing",
            )

            raise HTTPException(
                status_code=400,
                detail="thread_id is required",
            )

        log_event(
            logger,
            level=logging.INFO,
            event="chat_request_validated",
            request_id=request_id,
            thread_id=thread_id,
        )

        # ----------------------------------------------------
        # INPUT SECURITY
        # ----------------------------------------------------

        input_safe = await check_input(
            query
        )

        if not input_safe:

            latency_ms = round(
                (
                    perf_counter()
                    - request_started
                )
                * 1000,
                2,
            )

            log_event(
                logger,
                level=logging.WARNING,
                event="chat_request_blocked",
                request_id=request_id,
                thread_id=thread_id,
                stage="input",
                reason="security_guardrail",
                latency_ms=latency_ms,
                status="blocked",
            )

            return {
                "success": False,
                "blocked": True,
                "stage": "input",
                "reason": (
                    "Input blocked by "
                    "security guardrail"
                ),
            }

        # ----------------------------------------------------
        # LANGGRAPH CONFIG
        # ----------------------------------------------------

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        # ----------------------------------------------------
        # LANGGRAPH EXECUTION
        # ----------------------------------------------------

        graph_started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            event="graph_execution_started",
            request_id=request_id,
            thread_id=thread_id,
        )

        if graph is None:

            log_event(
                logger,
                level=logging.ERROR,
                event="graph_execution_failed",
                request_id=request_id,
                thread_id=thread_id,
                reason="graph_not_initialized",
            )

            raise HTTPException(
                status_code=503,
                detail="Application is not ready",
            )

        result = await graph.ainvoke(
            {
                "query": query
            },
            config=config,
        )

        graph_latency_ms = round(
            (
                perf_counter()
                - graph_started
            )
            * 1000,
            2,
        )

        route = result.get(
            "route"
        )

        log_event(
            logger,
            level=logging.INFO,
            event="graph_execution_completed",
            request_id=request_id,
            thread_id=thread_id,
            route=route,
            latency_ms=graph_latency_ms,
            status="success",
        )

        # ----------------------------------------------------
        # HUMAN APPROVAL REQUIRED
        # ----------------------------------------------------

        if "__interrupt__" in result:

            interrupt_data = (
                result[
                    "__interrupt__"
                ][0].value
            )

            latency_ms = round(
                (
                    perf_counter()
                    - request_started
                )
                * 1000,
                2,
            )

            log_event(
                logger,
                level=logging.INFO,
                event="email_approval_requested",
                request_id=request_id,
                thread_id=thread_id,
                route=route,
                latency_ms=latency_ms,
                status="approval_required",
            )

            return {
                "success": True,
                "blocked": False,
                "status": "approval_required",
                "thread_id": thread_id,
                "approval": interrupt_data,
            }

        # ----------------------------------------------------
        # PROCESS GRAPH RESPONSE
        # ----------------------------------------------------

        if route == "blog":

            blog_data = result.get(
                "blog",
                {},
            )

            title = blog_data.get(
                "title",
                "",
            )

            content = blog_data.get(
                "content",
                "",
            )

            response = (
                f"# {title}\n\n"
                f"{content}"
            )

        elif route == "email":

            response = result.get(
                "response",
                "Email completed successfully.",
            )

        else:

            response = (
                "Request completed successfully."
            )

        log_event(
            logger,
            level=logging.INFO,
            event="graph_response_created",
            request_id=request_id,
            thread_id=thread_id,
            route=route,
        )

        # ----------------------------------------------------
        # OUTPUT SECURITY
        # ----------------------------------------------------

        output_safe = await check_output(
            response
        )

        if not output_safe:

            latency_ms = round(
                (
                    perf_counter()
                    - request_started
                )
                * 1000,
                2,
            )

            log_event(
                logger,
                level=logging.WARNING,
                event="chat_request_blocked",
                request_id=request_id,
                thread_id=thread_id,
                route=route,
                stage="output",
                reason="security_guardrail",
                latency_ms=latency_ms,
                status="blocked",
            )

            return {
                "success": False,
                "blocked": True,
                "stage": "output",
                "reason": (
                    "Generated response blocked "
                    "by security guardrail"
                ),
            }

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        latency_ms = round(
            (
                perf_counter()
                - request_started
            )
            * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            event="chat_request_completed",
            request_id=request_id,
            thread_id=thread_id,
            route=route,
            latency_ms=latency_ms,
            status="success",
        )

        return {
            "success": True,
            "blocked": False,
            "status": "completed",
            "data": {
                "response": response,
                "route": route,
                "query": result.get(
                    "query"
                ),
                "thread_id": thread_id,
            },
        }

    except HTTPException:
        raise

    except Exception:

        latency_ms = round(
            (
                perf_counter()
                - request_started
            )
            * 1000,
            2,
        )

        logger.exception(
            "Chat request failed",
            extra={
                "event": "chat_request_failed",
                "context": {
                    "request_id": request_id,
                    "thread_id": thread_id,
                    "latency_ms": latency_ms,
                },
            },
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


# ============================================================
# EMAIL APPROVAL ENDPOINT
# ============================================================

@app.post("/email/approval")
async def email_approval(
    request: Request,
):

    request_id = str(uuid4())
    request_started = perf_counter()

    thread_id = None

    log_event(
        logger,
        level=logging.INFO,
        event="email_approval_request_started",
        request_id=request_id,
    )

    try:

        # ----------------------------------------------------
        # PARSE REQUEST
        # ----------------------------------------------------

        data = await request.json()

        thread_id = data.get(
            "thread_id"
        )

        decision = data.get(
            "decision"
        )

        # ----------------------------------------------------
        # VALIDATE THREAD
        # ----------------------------------------------------

        if not thread_id:

            log_event(
                logger,
                level=logging.WARNING,
                event="email_approval_validation_failed",
                request_id=request_id,
                reason="thread_id_missing",
            )

            raise HTTPException(
                status_code=400,
                detail="thread_id is required",
            )

        # ----------------------------------------------------
        # VALIDATE DECISION
        # ----------------------------------------------------

        if decision not in [
            "approve",
            "reject",
        ]:

            log_event(
                logger,
                level=logging.WARNING,
                event="email_approval_validation_failed",
                request_id=request_id,
                thread_id=thread_id,
                reason="invalid_decision",
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    "decision must be "
                    "'approve' or 'reject'"
                ),
            )

        # ----------------------------------------------------
        # HUMAN DECISION
        # ----------------------------------------------------

        log_event(
            logger,
            level=logging.INFO,
            event="email_approval_decision_received",
            request_id=request_id,
            thread_id=thread_id,
            decision=decision,
        )

        # ----------------------------------------------------
        # RESUME LANGGRAPH
        # ----------------------------------------------------

        if graph is None:

            log_event(
                logger,
                level=logging.ERROR,
                event="graph_resume_failed",
                request_id=request_id,
                thread_id=thread_id,
                reason="graph_not_initialized",
            )

            raise HTTPException(
                status_code=503,
                detail="Application is not ready",
            )

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        resume_started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            event="graph_resume_started",
            request_id=request_id,
            thread_id=thread_id,
            decision=decision,
        )

        result = await graph.ainvoke(
            Command(
                resume=decision
            ),
            config=config,
        )

        resume_latency_ms = round(
            (
                perf_counter()
                - resume_started
            )
            * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            event="graph_resume_completed",
            request_id=request_id,
            thread_id=thread_id,
            decision=decision,
            latency_ms=resume_latency_ms,
            status="success",
        )

        # ----------------------------------------------------
        # REJECT
        # ----------------------------------------------------

        if decision == "reject":

            latency_ms = round(
                (
                    perf_counter()
                    - request_started
                )
                * 1000,
                2,
            )

            log_event(
                logger,
                level=logging.INFO,
                event="email_rejected",
                request_id=request_id,
                thread_id=thread_id,
                latency_ms=latency_ms,
                status="rejected",
            )

            return {
                "success": True,
                "blocked": False,
                "status": "rejected",
                "thread_id": thread_id,
                "message": (
                    "Email rejected. "
                    "Nothing was sent."
                ),
            }

        # ----------------------------------------------------
        # APPROVED
        # ----------------------------------------------------

        log_event(
            logger,
            level=logging.INFO,
            event="email_approved",
            request_id=request_id,
            thread_id=thread_id,
        )

        # ----------------------------------------------------
        # ANOTHER INTERRUPT
        # ----------------------------------------------------

        if "__interrupt__" in result:

            interrupt_data = (
                result[
                    "__interrupt__"
                ][0].value
            )

            log_event(
                logger,
                level=logging.INFO,
                event="email_approval_requested",
                request_id=request_id,
                thread_id=thread_id,
                reason="additional_approval_required",
            )

            return {
                "success": True,
                "blocked": False,
                "status": "approval_required",
                "thread_id": thread_id,
                "approval": interrupt_data,
            }

        # ----------------------------------------------------
        # EMAIL RESPONSE
        # ----------------------------------------------------

        response = result.get(
            "response",
            "Email sent successfully.",
        )

        # ----------------------------------------------------
        # OUTPUT SECURITY
        # ----------------------------------------------------

        output_safe = await check_output(
            response
        )

        if not output_safe:

            latency_ms = round(
                (
                    perf_counter()
                    - request_started
                )
                * 1000,
                2,
            )

            log_event(
                logger,
                level=logging.WARNING,
                event="email_approval_blocked",
                request_id=request_id,
                thread_id=thread_id,
                stage="output",
                reason="security_guardrail",
                latency_ms=latency_ms,
                status="blocked",
            )

            return {
                "success": False,
                "blocked": True,
                "stage": "output",
                "thread_id": thread_id,
                "reason": (
                    "Generated response blocked "
                    "by security guardrail"
                ),
            }

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        latency_ms = round(
            (
                perf_counter()
                - request_started
            )
            * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            event="email_approval_request_completed",
            request_id=request_id,
            thread_id=thread_id,
            decision="approve",
            route=result.get("route"),
            latency_ms=latency_ms,
            status="success",
        )

        return {
            "success": True,
            "blocked": False,
            "status": "completed",
            "thread_id": thread_id,
            "data": {
                "response": response,
                "route": result.get(
                    "route"
                ),
            },
        }

    except HTTPException:
        raise

    except Exception:

        latency_ms = round(
            (
                perf_counter()
                - request_started
            )
            * 1000,
            2,
        )

        logger.exception(
            "Email approval request failed",
            extra={
                "event": (
                    "email_approval_request_failed"
                ),
                "context": {
                    "request_id": request_id,
                    "thread_id": thread_id,
                    "latency_ms": latency_ms,
                },
            },
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        uvicorn.Server(
            uvicorn.Config(
                app,
                host="0.0.0.0",
                port=8000,
                loop="asyncio",
            )
        ).serve(),
        loop_factory=asyncio.SelectorEventLoop,
    )