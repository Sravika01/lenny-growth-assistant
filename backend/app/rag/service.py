from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.factory import get_llm_provider
from app.rag.retriever import retrieve_relevant_chunks
from app.skills.rag_prompt import build_rag_prompt


def format_context(results: list[dict]) -> str:
    if not results:
        return ""

    context_parts = []

    for result in results:
        source = result["source"]

        citation = (
            f"[Episode: {source['episode']}, "
            f"Guest: {source['guest'] or 'Unknown'}, "
            f"{source['timestamp'] or source['topic'] or 'Transcript'}]"
        )

        context_parts.append(
            f"{citation}\n{result['content']}"
        )

    return "\n\n".join(context_parts)


async def generate_rag_response(
    question: str,
    db: AsyncSession,
    provider_name: str | None = None,
    conversation_history: str = "",
) -> tuple[str, list[dict]]:

    results = await retrieve_relevant_chunks(question, db)

    if not results:
        return (
            "I do not have sufficient information in Lenny's podcast archive "
            "to answer this.",
            [],
        )

    context = format_context(results)

    prompt = build_rag_prompt(
        question=question,
        context=context,
        conversation_history=conversation_history,
    )

    provider = get_llm_provider(provider_name)

    answer = await provider.generate(prompt)

    sources = [
        result["source"]
        for result in results
    ]

    return answer, sources