import os
import uuid
import asyncio


import uvicorn
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from langgraph.types import Command
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from src.graphs.graph_builder import GraphBuilder
from src.gateway.llm_gateway import LLMGateway
from src.guardrails.guardrail import (
    check_input,
    check_output,
)


load_dotenv()


# ============================================================
# LLM INITIALIZATION
# ============================================================

print("\n========== INITIALIZING LLM GATEWAY ==========")

llm_gateway = LLMGateway()

llm = llm_gateway.get_llm(
    model_name="primary",
    temperature=0.2,
)

print("✅ LLM Gateway initialized")
print("✅ Primary LLM initialized")


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

    database_url = os.getenv("DATABASE_URL")

    if not database_url:

        raise RuntimeError(
            "DATABASE_URL environment variable "
            "is not configured."
        )

    print(
        "\n========== INITIALIZING POSTGRES CHECKPOINTER =========="
    )

    async with AsyncPostgresSaver.from_conn_string(
        database_url
    ) as saver:

        # Initialize LangGraph PostgreSQL tables
        await saver.setup()

        checkpointer = saver

        print(
            "✅ PostgreSQL checkpointer initialized"
        )

        # Build LangGraph with persistent checkpointer
        graph_builder = GraphBuilder(
            llm,
            checkpointer
        )

        graph = graph_builder.setup_graph()

        print(
            "✅ LangGraph compiled with PostgreSQL persistence"
        )

        # Application runs while this context is alive
        yield

    # Cleanup after application shutdown
    graph = None
    checkpointer = None

    print(
        "✅ PostgreSQL checkpointer closed"
    )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Blog and Email Multi-Agent API",
    version="1.0.0",
    lifespan=lifespan
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

    try:

        # ----------------------------------------------------
        # Parse request
        # ----------------------------------------------------

        data = await request.json()

        query = data.get(
            "query",
            ""
        ).strip()

        if not query:

            raise HTTPException(
                status_code=400,
                detail="Query is required"
            )

        # ----------------------------------------------------
        # INPUT SECURITY
        # ----------------------------------------------------

        print(
            "\n========== INPUT SECURITY =========="
        )

        input_safe = await check_input(query)

        print(
            "INPUT SAFE:",
            input_safe
        )

        if input_safe is False:

            print(
                "🚫 INPUT BLOCKED"
            )

            return {
                "success": False,
                "blocked": True,
                "stage": "input",
                "reason": (
                    "Input blocked by "
                    "security guardrail"
                )
            }

        print(
            "✅ INPUT PASSED"
        )

        # ----------------------------------------------------
        # CREATE NEW WORKFLOW THREAD
        # ----------------------------------------------------

        thread_id = str(
            uuid.uuid4()
        )

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        # ----------------------------------------------------
        # LANGGRAPH EXECUTION
        # ----------------------------------------------------

        print(
            "\n========== LANGGRAPH =========="
        )

        result = await graph.ainvoke(
            {
                "query": query
            },
            config=config
        )

        print(
            "FULL GRAPH RESULT:"
        )

        print(result)

        # ----------------------------------------------------
        # HUMAN APPROVAL REQUIRED
        # ----------------------------------------------------

        if "__interrupt__" in result:

            interrupt_data = (
                result["__interrupt__"][0].value
            )

            print(
                "\n========== HUMAN APPROVAL =========="
            )

            print(
                "THREAD ID:",
                thread_id
            )

            print(
                "APPROVAL DATA:",
                interrupt_data
            )

            return {
                "success": True,
                "blocked": False,
                "status": "approval_required",
                "thread_id": thread_id,
                "approval": interrupt_data
            }

        # ----------------------------------------------------
        # PROCESS GRAPH RESPONSE
        # ----------------------------------------------------

        if result.get("route") == "blog":

            blog_data = result.get(
                "blog",
                {}
            )

            title = blog_data.get(
                "title",
                ""
            )

            content = blog_data.get(
                "content",
                ""
            )

            response = (
                f"# {title}\n\n"
                f"{content}"
            )

        elif result.get("route") == "email":

            response = result.get(
                "response",
                "Email completed successfully."
            )

        else:

            response = (
                "Request completed successfully."
            )

        # ----------------------------------------------------
        # GRAPH RESPONSE
        # ----------------------------------------------------

        print(
            "\n========== GRAPH RESPONSE =========="
        )

        print(response)

        # ----------------------------------------------------
        # OUTPUT SECURITY
        # ----------------------------------------------------

        print(
            "\n========== OUTPUT SECURITY =========="
        )

        output_safe = await check_output(
            response
        )

        print(
            "OUTPUT SAFE:",
            output_safe
        )

        if output_safe is False:

            print(
                "🚫 OUTPUT BLOCKED"
            )

            return {
                "success": False,
                "blocked": True,
                "stage": "output",
                "reason": (
                    "Generated response blocked "
                    "by security guardrail"
                )
            }

        print(
            "✅ OUTPUT PASSED"
        )

        # ----------------------------------------------------
        # SUCCESS RESPONSE
        # ----------------------------------------------------

        return {
            "success": True,
            "blocked": False,
            "status": "completed",
            "data": {
                "response": response,
                "route": result.get("route"),
                "query": result.get("query"),
                "thread_id": thread_id
            }
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            "\nCHAT ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ============================================================
# EMAIL APPROVAL ENDPOINT
# ============================================================

@app.post("/email/approval")
async def email_approval(
    request: Request
):

    try:

        # ----------------------------------------------------
        # Parse request
        # ----------------------------------------------------

        data = await request.json()

        thread_id = data.get(
            "thread_id"
        )

        decision = data.get(
            "decision"
        )

        # ----------------------------------------------------
        # Validate thread ID
        # ----------------------------------------------------

        if not thread_id:

            raise HTTPException(
                status_code=400,
                detail="thread_id is required"
            )

        # ----------------------------------------------------
        # Validate decision
        # ----------------------------------------------------

        if decision not in [
            "approve",
            "reject"
        ]:

            raise HTTPException(
                status_code=400,
                detail=(
                    "decision must be "
                    "'approve' or 'reject'"
                )
            )

        # ----------------------------------------------------
        # HUMAN DECISION
        # ----------------------------------------------------

        print(
            "\n========== HUMAN DECISION =========="
        )

        print(
            "THREAD ID:",
            thread_id
        )

        print(
            "DECISION:",
            decision
        )

        # ----------------------------------------------------
        # RESUME EXISTING LANGGRAPH THREAD
        # ----------------------------------------------------

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        result = await graph.ainvoke(
            Command(
                resume=decision
            ),
            config=config
        )

        print(
            "\n========== RESUMED GRAPH =========="
        )

        print(result)

        # ----------------------------------------------------
        # REJECT
        # ----------------------------------------------------

        if decision == "reject":

            print(
                "❌ EMAIL REJECTED"
            )

            return {
                "success": True,
                "blocked": False,
                "status": "rejected",
                "thread_id": thread_id,
                "message": (
                    "Email rejected. "
                    "Nothing was sent."
                )
            }

        # ----------------------------------------------------
        # APPROVE
        # ----------------------------------------------------

        print(
            "✅ EMAIL APPROVED"
        )

        # ----------------------------------------------------
        # ANOTHER INTERRUPT
        # ----------------------------------------------------

        if "__interrupt__" in result:

            interrupt_data = (
                result["__interrupt__"][0].value
            )

            return {
                "success": True,
                "blocked": False,
                "status": "approval_required",
                "thread_id": thread_id,
                "approval": interrupt_data
            }

        # ----------------------------------------------------
        # EMAIL RESPONSE
        # ----------------------------------------------------

        response = result.get(
            "response",
            "Email sent successfully."
        )

        # ----------------------------------------------------
        # OUTPUT SECURITY
        # ----------------------------------------------------

        output_safe = await check_output(
            response
        )

        if output_safe is False:

            print(
                "🚫 OUTPUT BLOCKED"
            )

            return {
                "success": False,
                "blocked": True,
                "stage": "output",
                "thread_id": thread_id,
                "reason": (
                    "Generated response blocked "
                    "by security guardrail"
                )
            }

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        return {
            "success": True,
            "blocked": False,
            "status": "completed",
            "thread_id": thread_id,
            "data": {
                "response": response,
                "route": result.get("route")
            }
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            "\nAPPROVAL ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
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
                loop="asyncio"
            )
        ).serve(),
        loop_factory=asyncio.SelectorEventLoop
    )
    
    

