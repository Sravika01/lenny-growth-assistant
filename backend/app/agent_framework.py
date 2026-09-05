from sqlalchemy.ext.asyncio import AsyncSession

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_ollama import ChatOllama

from app.config import settings
from app.rag.retriever import retrieve_relevant_chunks


SYSTEM_PROMPT = """
You are The Lenny Growth Assistant.

You answer product, growth, startup, leadership, and
product-management questions using Lenny's Podcast transcripts.

IMPORTANT RULES:

1. Always use the transcript search tool before answering
   factual questions about Lenny's Podcast.

2. Use ONLY information returned by the transcript search tool.

3. Do not invent facts, guests, statistics, quotes, or stories.

4. Cite transcript-supported claims.

5. Use this citation format:

   [Episode: Guest Name, Timestamp/Topic]

6. If the transcript search does not provide sufficient
   information, say exactly:

   "I do not have sufficient information in Lenny's podcast archive to answer this."

7. Use previous conversation context when answering follow-up questions.

8. Be useful, clear, and concise.

9. Do not use outside knowledge to answer questions about
   Lenny's Podcast.
"""


def build_agent(
    db: AsyncSession,
    provider_name: str | None = None,
):
    """
    Build the Lenny Growth Assistant agent with
    transcript retrieval as its tool.
    """

    provider = provider_name or settings.default_llm_provider

    @tool
    async def search_lenny_transcripts(query: str) -> str:
        """
        Search Lenny's Podcast transcript archive for
        information relevant to the user's question.
        """

        results = await retrieve_relevant_chunks(
            query=query,
            db=db,
            top_k=5,
        )

        if not results:
            return (
                "NO_RELEVANT_TRANSCRIPTS_FOUND. "
                "There is not enough relevant information "
                "in the Lenny's Podcast archive."
            )

        context_parts = []

        for result in results:
            source = result["source"]

            citation = (
                f"[Episode: {source['episode']}, "
                f"Guest: {source['guest'] or 'Unknown'}, "
                f"{source['timestamp'] or source['topic'] or 'Transcript'}]"
            )

            context_parts.append(
                f"{citation}\n"
                f"{result['content']}"
            )

        return "\n\n".join(context_parts)

    if provider == "ollama":

        model = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )

    elif provider == "anthropic":

        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not configured"
            )

        from langchain_anthropic import ChatAnthropic

        model = ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=0,
            max_tokens=1024,
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )

    agent = create_agent(
        model=model,
        tools=[
            search_lenny_transcripts,
        ],
        system_prompt=SYSTEM_PROMPT,
        name="lenny_growth_assistant",
    )

    return agent