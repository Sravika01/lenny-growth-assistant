from pathlib import Path

from sqlalchemy import delete

from app.database import AsyncSessionLocal
from app.models.db_models import TranscriptChunk
from app.rag.embeddings import create_embedding


TRANSCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "transcripts"
)

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        ).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def extract_metadata(
    file_path: Path,
    text: str,
) -> dict:

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    episode = file_path.parent.name

    guest = None

    for line in lines[:30]:

        lower = line.lower()

        if "guest:" in lower:
            guest = line.split(
                ":",
                1,
            )[1].strip()

            break

        if "guest" in lower and "#" not in lower:
            guest = line[:255]
            break

    if guest is None:
        guest = episode.replace(
            "-",
            " ",
        ).title()

    return {
        "episode": episode,
        "guest": guest,
        "timestamp": None,
        "topic": None,
        "source_file": str(
            file_path.relative_to(
                TRANSCRIPTS_DIR.parent.parent
            )
        ),
    }


async def ingest():

    transcript_files = list(
        TRANSCRIPTS_DIR.rglob("*.md")
    )

    transcript_files = [
        path
        for path in transcript_files
        if path.name.lower() != "readme.md"
    ]

    print(
        f"Found {len(transcript_files)} transcript files."
    )

    async with AsyncSessionLocal() as db:

        await db.execute(
            delete(TranscriptChunk)
        )

        await db.commit()

        total_chunks = 0

        for file_path in transcript_files:

            print(
                f"Processing: {file_path}"
            )

            text = file_path.read_text(
                encoding="utf-8"
            )

            if not text.strip():
                continue

            metadata = extract_metadata(
                file_path,
                text,
            )

            chunks = split_text(text)

            for chunk_text in chunks:

                embedding = create_embedding(
                    chunk_text
                )

                chunk = TranscriptChunk(
                    content=chunk_text,
                    episode=metadata["episode"],
                    guest=metadata["guest"],
                    timestamp=metadata["timestamp"],
                    topic=metadata["topic"],
                    source_file=metadata["source_file"],
                    embedding=embedding,
                )

                db.add(chunk)

                total_chunks += 1

        await db.commit()

    print(
        f"Ingestion complete. Created {total_chunks} chunks."
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(ingest())