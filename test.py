from src.gateway.llm_gateway import LLMGateway


def main():

    print("🚀 Initializing LLM Gateway...")

    gateway = LLMGateway()

    print("✅ Gateway initialized")

    llm = gateway.get_llm()

    print("✅ LLM created")

    response = llm.invoke(
        "Explain what an LLM Gateway is in one sentence."
    )

    print("\n🤖 Response:")
    print(response.content)


if __name__ == "__main__":
    main()