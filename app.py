import uvicorn
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from langgraph.types import Command

from src.graphs.graph_builder import GraphBuilder
from src.gateway.llm_gateway import LLMGateway
from src.guardrails.guardrail import (
    check_input,
    check_output,
)


load_dotenv()


app = FastAPI(
    title="Blog and Email Multi-Agent API",
    version="1.0.0"
)



print("\n========== INITIALIZING LLM GATEWAY ==========")

llm_gateway = LLMGateway()

llm = llm_gateway.get_llm(
    model_name="primary",
    temperature=0.2,
)

print("✅ LLM Gateway initialized")
print("✅ Primary LLM initialized")




graph_builder = GraphBuilder(llm)

graph = graph_builder.setup_graph()




@app.get("/")
async def root():

    return {
        "message": "Multi-Agent AI System is running"
    }




@app.post("/chat")
async def chat(request: Request):

    try:

        

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


        
        thread_id = str(
            uuid.uuid4()
        )

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }



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



        print(
            "\n========== GRAPH RESPONSE =========="
        )

        print(response)



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
            "ERROR:",
            str(e)
        )

        return {
            "success": False,
            "blocked": False,
            "error": str(e)
        }




@app.post("/email/approval")
async def email_approval(
    request: Request
):

    try:

       

        data = await request.json()

        thread_id = data.get(
            "thread_id"
        )

        decision = data.get(
            "decision"
        )


        if not thread_id:

            raise HTTPException(
                status_code=400,
                detail="thread_id is required"
            )


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



        print(
            "✅ EMAIL APPROVED"
        )


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


        response = result.get(
            "response",
            "Email sent successfully."
        )


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

        return {
            "success": False,
            "blocked": False,
            "status": "error",
            "error": str(e)
        }



if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
    
    

