from src.gateway.llm_gateway import LLMGateway
from src.graphs.graph_builder import GraphBuilder


# Initialize LLM Gateway
gateway = LLMGateway()

# Get the configured LLM
llm = gateway.get_llm()

# Build graph
graph_builder = GraphBuilder(llm)

# Compile graph
graph = graph_builder.setup_graph()