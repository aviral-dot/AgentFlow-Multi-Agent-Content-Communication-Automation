

from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM

from .dataset import BLOG_TEST_CASES
from .metrics import blog_quality, title_relevancy


def get_blog_graph():

    llm = GroqLLM().get_llm()

    graph_builder = GraphBuilder(llm)

    graph = graph_builder.setup_graph()

    return graph


def test_blog_generation():

    graph = get_blog_graph()

    for test_data in BLOG_TEST_CASES:

        query = test_data["query"]

        
        result = graph.invoke(
            {
                "query": query
            }
        )

       
        assert "blog" in result

        blog = result["blog"]

        
        assert blog["title"].strip() != ""
        assert blog["content"].strip() != ""

       

        title_test_case = LLMTestCase(
            input=query,
            actual_output=blog["title"]
        )

        assert_test(
            title_test_case,
            [title_relevancy]
        )

      

        content_test_case = LLMTestCase(
            input=query,
            actual_output=blog["content"]
        )

        assert_test(
            content_test_case,
            [blog_quality]
        )