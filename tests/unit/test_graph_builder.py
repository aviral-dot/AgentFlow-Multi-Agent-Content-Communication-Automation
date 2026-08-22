
from src.graphs.graph_builder import GraphBuilder


def test_route_request_to_blog(fake_llm):
    builder = GraphBuilder(fake_llm, checkpointer=None)

    state = {
        "route": "blog"
    }

    result = builder.route_request(state)

    assert result == "blog"


def test_route_request_to_email(fake_llm):
    builder = GraphBuilder(fake_llm, checkpointer=None)

    state = {
        "route": "email"
    }

    result = builder.route_request(state)

    assert result == "email"


def test_approval_routes_to_send_email(fake_llm):
    builder = GraphBuilder(fake_llm, checkpointer=None)

    state = {
        "approval": "approve"
    }

    result = builder.route_after_approval(state)

    assert result == "send_email"


def test_approval_rejected_routes_to_end(fake_llm):
    builder = GraphBuilder(fake_llm, checkpointer=None)

    state = {
        "approval": "reject"
    }

    result = builder.route_after_approval(state)

    assert result == "end"


def test_graph_is_built(fake_llm):
    builder = GraphBuilder(fake_llm, checkpointer=None)

    graph = builder.build_graph()

    assert graph is not None