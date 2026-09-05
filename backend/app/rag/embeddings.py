from app.config import settings


def create_embedding(text: str) -> list[float]:
    if settings.default_llm_provider.lower() == "gemini":
        return create_gemini_embedding(text)

    return create_local_embedding(text)


def create_local_embedding(text: str) -> list[float]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def create_gemini_embedding(text: str) -> list[float]:
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=384,
            task_type="RETRIEVAL_DOCUMENT",
        ),
    )

    return result.embeddings[0].values