from litellm import Router

from langchain_litellm import ChatLiteLLMRouter

from src.gateway.config import LLMGatewayConfig


class LLMGateway:
    """
    Central LLM Gateway for AgentFlow.

    All application agents obtain their LLM through this class.
    Agents never directly depend on Groq/OpenAI/etc.
    """

    def __init__(self):
        LLMGatewayConfig.validate()

        self.model_list = [
            {
                "model_name": "primary",
                "litellm_params": {
                    "model": LLMGatewayConfig.PRIMARY_MODEL,
                    "api_key": self._get_api_key(
                        LLMGatewayConfig.PRIMARY_MODEL
                    ),
                }
            }
        ]

        fallbacks = []

        if self._fallback_available():

            self.model_list.append(
                {
                    "model_name": "fallback",
                    "litellm_params": {
                        "model": LLMGatewayConfig.FALLBACK_MODEL,
                        "api_key": self._get_api_key(
                            LLMGatewayConfig.FALLBACK_MODEL
                        ),
                    }
                }
            )

            fallbacks = [
                {
                    "primary": [
                        "fallback"
                    ]
                }
            ]

        self.router = Router(
            model_list=self.model_list,
            routing_strategy=(
                LLMGatewayConfig.ROUTING_STRATEGY
            ),
            num_retries=(
                LLMGatewayConfig.NUM_RETRIES
            ),
            timeout=(
                LLMGatewayConfig.TIMEOUT
            ),
            fallbacks=fallbacks,
        )

        self._models = {}

    @staticmethod
    def _get_api_key(model: str):
        """Return the correct API key for a model."""

        if model.startswith("groq/"):
            import os

            return os.getenv(
                "GROQ_API_KEY"
            )

        if model.startswith("gemini/"):
            import os

            return os.getenv(
                "GEMINI_API_KEY"
            )

        return None

    @staticmethod
    def _fallback_available():
        import os

        return bool(
            os.getenv("GEMINI_API_KEY")
        )

    def get_llm(
        self,
        model_name: str = "primary",
        temperature: float = 0.2,
    ):
        """
        Return a LangChain-compatible LLM
        backed by the LiteLLM Router.
        """

        cache_key = (
            model_name,
            temperature,
        )

        if cache_key not in self._models:

            self._models[cache_key] = (
                ChatLiteLLMRouter(
                    router=self.router,
                    model_name=model_name,
                    temperature=temperature,
                )
            )

        return self._models[cache_key]