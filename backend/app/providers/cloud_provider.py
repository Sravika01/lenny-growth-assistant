from typing import AsyncIterator

from openai import AsyncOpenAI

from app.providers.base import LLMProvider


class CloudProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self.model = model

    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=2048,
        )

        return response.choices[0].message.content or ""

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=2048,
            stream=True,
        )

        async for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                yield text