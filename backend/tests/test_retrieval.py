from app.rag.retriever import MIN_SIMILARITY, TOP_K


def test_retrieval_configuration():
    assert TOP_K == 5
    assert MIN_SIMILARITY > 0
    assert MIN_SIMILARITY < 1