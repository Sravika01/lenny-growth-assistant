import asyncio

from app.agent_framework import build_agent
from app.database import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as db:

        agent = build_agent(
            db=db,
            provider_name="ollama",
        )

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "What does Lenny's Podcast say about "
                            "product-market fit?"
                        ),
                    }
                ]
            }
        )

        print("\n========== AGENT RESPONSE ==========\n")

        messages = result.get("messages", [])

        if messages:
            print(messages[-1].content)
        else:
            print("No response returned.")


if __name__ == "__main__":
    asyncio.run(main())