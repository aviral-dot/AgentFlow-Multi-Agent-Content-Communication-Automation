from src.states.blogstate import AgentState

class BlogNode:
    """
    A class to represent he blog node
    """

    def __init__(self,llm):
        self.llm=llm

    
    async def title_creation(self,state:AgentState):
        """
        create the title for the blog
        """

        if "query" in state and state["query"]:
            prompt="""
                   You are an expert blog content writer. Use Markdown formatting. Generate
                   a blog title for the {query}. This title should be creative and SEO friendly

                   """
            
            sytem_message=prompt.format(query=state["query"])
            print(sytem_message)
            response=await self.llm.ainvoke(sytem_message)
            print(response)
            return {"blog":{"title":response.content}}
        
    async def content_generation(self,state:AgentState):
        if "query" in state and state["query"]:
            system_prompt = """You are expert blog writer. Use Markdown formatting.
            Generate a detailed blog content with detailed breakdown for the {query}"""
            system_message = system_prompt.format(query=state["query"])
            response =await self.llm.ainvoke(system_message)
            return {"blog": {"title": state['blog']['title'], "content": response.content}}