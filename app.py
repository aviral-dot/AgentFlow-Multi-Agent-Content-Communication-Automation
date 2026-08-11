import os
from dotenv import load_dotenv
import uvicorn



from fastapi import FastAPI, HTTPException, Request



from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM




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


       

        result = await graph.ainvoke(
            {
                "query": query
            }
        )


      

        response = result.get(
            "response",
            ""
        )


        if not response:

            response = "Request completed successfully."





        return {
            "success": True,
            "blocked": False,
            "data": result
        }


   

    except HTTPException:

        raise


    

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }



if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
