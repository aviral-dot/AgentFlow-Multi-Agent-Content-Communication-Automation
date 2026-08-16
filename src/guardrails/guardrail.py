from pathlib import Path

from dotenv import load_dotenv
from nemoguardrails import RailsConfig, LLMRails




PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")




GUARDRAIL_DIR = Path(__file__).resolve().parent

config = RailsConfig.from_path(
    str(GUARDRAIL_DIR)
)

rails = LLMRails(config)




async def check_input(text: str) -> bool:

    result = await rails.generate_async(
        messages=[
            {
                "role": "user",
                "content": text,
            }
        ]
    )

    print("\n========== RAW INPUT GUARDRAIL ==========")
    print(result)



    if result.get("role") == "exception":

        exception_content = result.get(
            "content",
            {}
        )

        exception_type = exception_content.get(
            "type",
            ""
        )

        if exception_type == "InputRailException":

            print("🚫 INPUT BLOCKED")

            return False

    

    print("✅ INPUT ALLOWED")

    return True




async def check_output(text: str) -> bool:

    result = await rails.generate_async(
        messages=[
            {
                "role": "assistant",
                "content": text,
            }
        ]
    )

    print("\n========== RAW OUTPUT GUARDRAIL ==========")
    print(result)

    

    if result.get("role") == "exception":

        exception_content = result.get(
            "content",
            {}
        )

        exception_type = exception_content.get(
            "type",
            ""
        )

        if exception_type == "OutputRailException":

            print("🚫 OUTPUT BLOCKED")

            return False

    

    print("✅ OUTPUT ALLOWED")

    return True