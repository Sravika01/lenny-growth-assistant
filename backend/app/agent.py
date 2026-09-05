from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.service import generate_rag_response
from app.rag.retriever import retrieve_relevant_chunks
from app.skills.ship30_writer import build_ship30_prompt
from app.skills.artifact_generator import is_html_artifact_request
from app.providers.factory import get_llm_provider


HTML_ARTIFACT_PROMPT = """
You are the HTML Artifact Generator inside The Lenny Growth Assistant.

Create a complete, self-contained HTML page based ONLY on the provided
Lenny's Podcast transcript context.

Requirements:

1. Return a complete HTML document.
2. Include HTML, head, body and CSS.
3. CSS must be inside a <style> tag.
4. Do not use external JavaScript libraries.
5. Do not use external resources.
6. Keep the design clean and professional.
7. Use only information supported by the transcript context.
8. Do not invent facts, statistics, quotes or claims.
9. Include transcript citations where appropriate.
10. The output must be suitable for display inside a sandboxed iframe.
11. Do not include markdown code fences.
12. Return ONLY the HTML artifact using these exact tags:

<artifact type="html" title="Generated HTML">
<!DOCTYPE html>
<html>
...
</html>
</artifact>
"""


def format_context(results: list[dict]) -> str:
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


async def run_agent(
    message: str,
    db: AsyncSession,
    provider_name: str | None = None,
    conversation_history: str = "",
) -> tuple[str, list[dict]]:

    lower_message = message.lower()

    # ---------------------------------------------------------
    # HTML ARTIFACT
    # ---------------------------------------------------------
    if is_html_artifact_request(message):

        results = await retrieve_relevant_chunks(
            message,
            db,
        )

        if not results:
            return (
                "I do not have sufficient information in Lenny's podcast "
                "archive to create this artifact.",
                [],
            )

        context = format_context(results)

        prompt = f"""
{HTML_ARTIFACT_PROMPT}

CONVERSATION HISTORY:
{conversation_history}

TRANSCRIPT CONTEXT:
{context}

USER REQUEST:
{message}

GENERATE THE HTML ARTIFACT NOW:
"""

        provider = get_llm_provider(provider_name)

        answer = await provider.generate(prompt)

        sources = [
            result["source"]
            for result in results
        ]

        return answer, sources

    # ---------------------------------------------------------
    # SHIP 30 FOR 30
    # ---------------------------------------------------------
    is_ship30_request = any(
        phrase in lower_message
        for phrase in [
            "ship 30",
            "30 for 30",
            "write an essay",
            "write a linkedin post",
            "turn this into an essay",
        ]
    )

    if is_ship30_request:

        results = await retrieve_relevant_chunks(
            message,
            db,
        )

        if not results:
            return (
                "I do not have sufficient information in Lenny's podcast "
                "archive to create this piece.",
                [],
            )

        context = format_context(results)

        prompt = build_ship30_prompt(
            topic=message,
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

    # ---------------------------------------------------------
    # NORMAL RAG QUESTION
    # ---------------------------------------------------------
    answer, sources = await generate_rag_response(
        question=message,
        db=db,
        provider_name=provider_name,
        conversation_history=conversation_history,
    )

    return answer, sources