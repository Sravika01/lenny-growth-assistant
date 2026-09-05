from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import TranscriptChunk
from app.rag.embeddings import create_embedding


TOP_K = 5
MIN_SIMILARITY = 0.25


async def retrieve_relevant_chunks(
    query: str,
    db: AsyncSession,
    top_k: int = TOP_K,
):
    # User questions must use RETRIEVAL_QUERY.
    # Transcript chunks were indexed using RETRIEVAL_DOCUMENT.
    query_embedding = create_embedding(
        query,
        task_type="RETRIEVAL_QUERY",
    )

    similarity = (
        1
        - TranscriptChunk.embedding.cosine_distance(
            query_embedding
        )
    )

    statement = (
        select(
            TranscriptChunk,
            similarity.label("similarity"),
        )
        .where(
            TranscriptChunk.embedding.is_not(None)
        )
        .order_by(similarity.desc())
        .limit(top_k)
    )

    result = await db.execute(statement)

    chunks = []

    for chunk, score in result.all():
        if score < MIN_SIMILARITY:
            continue

        chunks.append(
            {
                "content": chunk.content,
                "similarity": float(score),
                "source": {
                    "episode": chunk.episode,
                    "guest": chunk.guest,
                    "timestamp": chunk.timestamp,
                    "topic": chunk.topic,
                    "source_file": chunk.source_file,
                },
            }
        )

    return chunks