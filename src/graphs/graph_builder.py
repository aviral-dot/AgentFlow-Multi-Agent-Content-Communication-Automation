from langgraph.graph import StateGraph, START, END

from src.llms.groqllm import GroqLLM
from src.states.blogstate import AgentState
from langgraph.checkpoint.memory import InMemorySaver

from src.nodes.blog_node import BlogNode
from src.nodes.mail_node import EmailNode
from src.nodes.supervisor_node import SupervisorNode


class GraphBuilder:

    def __init__(self, llm):

        self.llm = llm

        
        self.graph = StateGraph(AgentState)

        
        self.blog_node = BlogNode(self.llm)
        self.email_node = EmailNode(self.llm)
        self.supervisor_node = SupervisorNode(self.llm)

    def build_graph(self):

       

        self.graph.add_node(
            "supervisor",
            self.supervisor_node.decide
        )

        
        self.graph.add_node(
            "title_creation",
            self.blog_node.title_creation
        )

        self.graph.add_node(
            "content_generation",
            self.blog_node.content_generation
        )

        
        self.graph.add_node(
            "draft_email",
            self.email_node.draft_email
        )

        self.graph.add_node(
           "approve_email",
           self.email_node.approve_email
        )

        self.graph.add_node(
            "send_email",
            self.email_node.send_email
        )

       

        self.graph.add_edge(
            START,
            "supervisor"
        )


        self.graph.add_conditional_edges(
            "supervisor",
            self.route_request,
            {
                "blog": "title_creation",
                "email": "draft_email"
            }
        )

   
        self.graph.add_edge(
            "title_creation",
            "content_generation"
        )

        self.graph.add_edge(
            "content_generation",
            END
        )


        # self.graph.add_edge(
        #     "draft_email",
        #     "send_email"
        # )

        self.graph.add_edge(
          "draft_email",
          "approve_email"
        )

        self.graph.add_conditional_edges(
           "approve_email",
           self.route_after_approval,
           {
              "send_email": "send_email",
               "end": END
            }
        )

        self.graph.add_edge(
            "send_email",
            END
        )

        return self.graph

  

    def route_request(self, state: AgentState):

        return state["route"]

    def route_after_approval(self, state: AgentState):

      if state["approval"] == "approve":
         return "send_email"

      return "end"

 

    def setup_graph(self):

        graph = self.build_graph()
        checkpointer = InMemorySaver()
        return graph.compile( checkpointer=checkpointer)



