import asyncio

from src.guardrails.guardrail import rails


async def main():

    result = await rails.generate_async(
        messages=[
            {
                "role": "user",
                "content": "Life is great."
            }
        ]
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
