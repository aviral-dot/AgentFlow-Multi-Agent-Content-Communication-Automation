import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


class GroqLLM:

    def __init__(self):
        load_dotenv()

    def get_llm(self):
        try:
            groq_api_key = os.getenv("GROQ_API_KEY")

            if not groq_api_key:
                raise ValueError(
                    "GROQ_API_KEY is not configured"
                )

            self.groq_api_key = groq_api_key

            return ChatGroq(
                api_key=self.groq_api_key,
                model="openai/gpt-oss-20b",
            )

        except ValueError:
            raise

        except Exception as e:
            raise ValueError(
                f"Failed to initialize Groq LLM: {e}"
            ) from e