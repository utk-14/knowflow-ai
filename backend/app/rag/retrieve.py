from fastapi import HTTPException
from app.rag.ingest import embed_texts
from app.db import supabase_admin


def retrieve_relevant_chunks(
    user_id: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Embed the query and return the top-K most similar chunks
    belonging to this user only.

    Each item: { "id": str, "content": str, "similarity": float }
    """
    if not query.strip():
        return []

    # 1. Embed the query with the query-specific task
    query_vectors = embed_texts([query], task="retrieval.query")
    if not query_vectors:
        raise HTTPException(status_code=500, detail="Failed to embed query")

    query_embedding = query_vectors[0]

    # 2. Call the Postgres function `match_chunks` we defined earlier
    #    This uses the ivfflat index for fast cosine-similarity search.
    response = supabase_admin.rpc(
        "match_chunks",
        {
            "query_embedding": query_embedding,
            "match_user_id": user_id,
            "match_count": top_k,
        },
    ).execute()

    if not response.data:
        return []

    return response.data