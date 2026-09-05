import json
from typing import AsyncIterator

import httpx

from app.config import settings
from app.providers.base import LLMProvider


class OllamaProvider(LLMProvider):

    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    async def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                )

            response.raise_for_status()

            data = response.json()

            return data["response"]

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Ollama is unavailable. Please make sure Ollama is running."
            ) from exc

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "Ollama request timed out. Please try again."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Ollama returned an error: {exc.response.status_code}"
            ) from exc

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=payload,
                ) as response:

                    response.raise_for_status()

                    async for line in response.aiter_lines():

                        if not line:
                            continue

                        data = json.loads(line)

                        if data.get("response"):
                            yield data["response"]

                        if data.get("done"):
                            break

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Ollama is unavailable. Please make sure Ollama is running."
            ) from exc

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "Ollama request timed out. Please try again."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Ollama returned an error: {exc.response.status_code}"
            ) from exc