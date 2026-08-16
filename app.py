import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM
from src.guardrails.guardrail import (
    check_input,
    check_output,
)

load_dotenv()

app = FastAPI(
    title="Blog and Email Multi-Agent API",
    version="1.0.0"
)


groqllm = GroqLLM()

llm = groqllm.get_llm()




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


    

        print("\n========== INPUT SECURITY ==========")

        input_safe = await check_input(query)

        print(
            "INPUT SAFE:",
            input_safe
        )


       

        if input_safe == False:

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


        
        print(
            "\n========== LANGGRAPH =========="
        )

        result = await graph.ainvoke(
            {
                "query": query
            }
        )

        print(
            "FULL GRAPH RESULT:"
        )

        print(result)



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

            email_data = result.get(
                "email",
                {}
            )

            response = email_data.get(
                "content",
                "Email generated successfully."
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


    

        if output_safe == False:

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
            "data": {
                "response": response,
                "route": result.get("route"),
                "query": result.get("query")
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




if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )



