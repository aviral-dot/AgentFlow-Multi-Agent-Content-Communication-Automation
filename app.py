import os
from dotenv import load_dotenv
import uvicorn



from fastapi import FastAPI, HTTPException, Request



from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Blog and Email Multi-Agent API",
    version="1.0.0"
)


# ============================================================
# LLM
# ============================================================

groqllm = GroqLLM()

llm = groqllm.get_llm()


# ============================================================
# LANGGRAPH
# ============================================================

graph_builder = GraphBuilder(llm)

graph = graph_builder.setup_graph()



# ============================================================
# HEALTH CHECK
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
        # READ REQUEST
        # ----------------------------------------------------

        data = await request.json()

        query = data.get(
            "query",
            ""
        ).strip()


        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if not query:

            raise HTTPException(
                status_code=400,
                detail="Query is required"
            )


       


        # ====================================================
        # STEP 2 — RUN LANGGRAPH
        # ====================================================

        result = await graph.ainvoke(
            {
                "query": query
            }
        )


        # ====================================================
        # STEP 3 — GET FINAL RESPONSE
        # ====================================================

        response = result.get(
            "response",
            ""
        )


        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if not response:

            response = "Request completed successfully."




        # ====================================================
        # STEP 5 — RETURN FINAL RESPONSE
        # ====================================================

        return {
            "success": True,
            "blocked": False,
            "data": result
        }


    # ========================================================
    # HTTP EXCEPTION
    # ========================================================

    except HTTPException:

        raise


    # ========================================================
    # GENERAL EXCEPTION
    # ========================================================

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
