import logging
import os

from langchain_litellm import ChatLiteLLMRouter
from litellm import Router

from src.gateway.config import LLMGatewayConfig
from src.utils.loggers import (
    get_logger,
    log_event,
)

logger = get_logger(__name__)


class LLMGateway:
    """
    Central LLM Gateway for AgentFlow.

    All application agents obtain their LLM through this class.
    Agents never directly depend on Groq/OpenAI/etc.
    """

    def __init__(self):

        log_event(
            logger,
            level=logging.INFO,
            event="llm_gateway_initialization_started",
        )

        try:

            LLMGatewayConfig.validate()

            self.model_list = [
                {
                    "model_name": "primary",
                    "litellm_params": {
                        "model": (
                            LLMGatewayConfig.PRIMARY_MODEL
                        ),
                        "api_key": self._get_api_key(
                            LLMGatewayConfig.PRIMARY_MODEL
                        ),
                    },
                }
            ]

            fallbacks = []

            fallback_available = (
                self._fallback_available()
            )

            if fallback_available:

                self.model_list.append(
                    {
                        "model_name": "fallback",
                        "litellm_params": {
                            "model": (
                                LLMGatewayConfig.FALLBACK_MODEL
                            ),
                            "api_key": self._get_api_key(
                                LLMGatewayConfig.FALLBACK_MODEL
                            ),
                        },
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

            log_event(
                logger,
                level=logging.INFO,
                event="llm_gateway_initialized",
                primary_model=(
                    LLMGatewayConfig.PRIMARY_MODEL
                ),
                fallback_enabled=fallback_available,
                routing_strategy=(
                    LLMGatewayConfig.ROUTING_STRATEGY
                ),
                retries=(
                    LLMGatewayConfig.NUM_RETRIES
                ),
                timeout=(
                    LLMGatewayConfig.TIMEOUT
                ),
                status="success",
            )

        except Exception:

            logger.exception(
                "LLM gateway initialization failed",
                extra={
                    "event": (
                        "llm_gateway_initialization_failed"
                    ),
                    "context": {},
                },
            )

            raise

    @staticmethod
    def _get_api_key(
        model: str,
    ):
        """
        Return the API key associated with a model.

        API keys are never logged.
        """

        if model.startswith("groq/"):

            return os.getenv(
                "GROQ_API_KEY"
            )

        if model.startswith("gemini/"):

            return os.getenv(
                "GEMINI_API_KEY"
            )

        return None

    @staticmethod
    def _fallback_available() -> bool:

        return bool(
            os.getenv(
                "GEMINI_API_KEY"
            )
        )

    def get_llm(
        self,
        model_name: str = "primary",
        temperature: float = 0.2,
    ):
        """
        Return a LangChain-compatible LLM
        backed by the LiteLLM Router.

        LLM clients are cached by model name
        and temperature.
        """

        cache_key = (
            model_name,
            temperature,
        )

        # ----------------------------------------------------
        # CACHE HIT
        # ----------------------------------------------------

        if cache_key in self._models:

            log_event(
                logger,
                level=logging.DEBUG,
                event="llm_client_cache_hit",
                model_name=model_name,
                temperature=temperature,
            )

            return self._models[
                cache_key
            ]

        # ----------------------------------------------------
        # CREATE LLM CLIENT
        # ----------------------------------------------------

        log_event(
            logger,
            level=logging.INFO,
            event="llm_client_creation_started",
            model_name=model_name,
            temperature=temperature,
        )

        try:

            llm = ChatLiteLLMRouter(
                router=self.router,
                model_name=model_name,
                temperature=temperature,
            )

            self._models[
                cache_key
            ] = llm

            log_event(
                logger,
                level=logging.INFO,
                event="llm_client_created",
                model_name=model_name,
                temperature=temperature,
                cache_size=len(
                    self._models
                ),
                status="success",
            )

            return llm

        except Exception:

            logger.exception(
                "LLM client creation failed",
                extra={
                    "event": "llm_client_creation_failed",
                    "context": {
                        "model_name": model_name,
                        "temperature": temperature,
                    },
                },
            )

            raise