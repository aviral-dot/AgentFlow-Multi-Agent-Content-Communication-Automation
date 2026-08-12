
import os
import uvicorn
import requests

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM



load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not NVIDIA_API_KEY:
    raise RuntimeError("NVIDIA_API_KEY is missing from .env")



app = FastAPI(
    title="Blog and Email Multi-Agent API",
    version="1.0.0"
)



groqllm = GroqLLM()

llm = groqllm.get_llm()




graph_builder = GraphBuilder(llm)

graph = graph_builder.setup_graph()



SAFETY_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

SAFETY_MODEL = "nvidia/nemotron-3.5-content-safety"


def check_content_safety(text: str) -> bool:

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": SAFETY_MODEL,
        "messages": [
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0,
        "max_tokens": 20
    }

    response = requests.post(
        SAFETY_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    safety_result = (
        result["choices"][0]["message"]["content"]
        .strip()
        .lower()
    )

    print("CONTENT SAFETY RESULT:", safety_result)

 

    if "unsafe" in safety_result:
        return False

    if "safe" in safety_result:
        return True

    
    return False




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


       

        print("\n========== INPUT SAFETY ==========")

        input_safe = check_content_safety(query)

        print("INPUT SAFE:", input_safe)


      

        if not input_safe:

            print("🚫 INPUT BLOCKED")

            return {
                "success": False,
                "blocked": True,
                "reason": "Input blocked by content safety guardrail"
            }


        print("✅ INPUT PASSED")


       
        print("\n========== LANGGRAPH ==========")

        result = await graph.ainvoke(
            {
                "query": query
            }
        )

        print("FULL GRAPH RESULT:")
        print(result)
      

        if result.get("route") == "blog":

            blog_data = result.get("blog", {})

            title = blog_data.get("title", "")
            content = blog_data.get("content", "")
 
            response = f"# {title}\n\n{content}"

        elif result.get("route") == "email":

            email_data = result.get("email", {})

            response = email_data.get(
              "content",
              "Email generated successfully."
            )

        else:

             response = "Request completed successfully."


        print("GRAPH RESPONSE:")
        print(response)


        

        print("\n========== OUTPUT SAFETY ==========")

        output_safe = check_content_safety(response)

        print("OUTPUT SAFE:", output_safe)


        

        if not output_safe:

            print("🚫 OUTPUT BLOCKED")

            return {
                "success": False,
                "blocked": True,
                "reason": "Output blocked by content safety guardrail"
            }


        print("✅ OUTPUT PASSED")


      

        return {
            "success": True,
            "blocked": False,
            "data": result
        }


    

    except HTTPException:

        raise


    
    except Exception as e:

        print("ERROR:", str(e))

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




