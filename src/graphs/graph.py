from src.database.postgres import create_checkpointer
from src.gateway.llm_gateway import LLMGateway
from src.graphs.graph_builder import GraphBuilder


# Initialize LLM Gateway
gateway = LLMGateway()

# Get the configured LLM
llm = gateway.get_llm()

# Create checkpointer
checkpointer = create_checkpointer()

# Build graph
graph_builder = GraphBuilder(
    llm,
    checkpointer,
)

# Compile graph
graph = graph_builder.setup_graph()