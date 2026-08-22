import os

from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCaseParams
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


class GroqEvalModel(DeepEvalBaseLLM):

    def __init__(self):
        self.model = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        response = self.model.invoke(prompt)
        return response.content

    async def a_generate(self, prompt: str) -> str:
        response = await self.model.ainvoke(prompt)
        return response.content

    def get_model_name(self):
        return "Groq Llama 3.1 8B Instant"


eval_model = GroqEvalModel()


title_relevancy = AnswerRelevancyMetric(
    threshold=0.8,
    model=eval_model,
    include_reason=True
)


blog_quality = GEval(
    name="Blog Quality",

    criteria="""
    Evaluate whether the generated blog:

    1. Directly addresses the user's requested topic.
    2. Is relevant to the topic.
    3. Is coherent and logically organized.
    4. Provides useful and sufficiently detailed information.
    5. Is clear and easy to understand.
    6. Uses appropriate Markdown formatting.
    """,

    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT
    ],

    threshold=0.8,
    model=eval_model,
)
