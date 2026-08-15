from pathlib import Path

from dotenv import load_dotenv
from nemoguardrails import RailsConfig, LLMRails


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


GUARDRAIL_DIR = Path(__file__).resolve().parent

config = RailsConfig.from_path(str(GUARDRAIL_DIR))

rails = LLMRails(config)