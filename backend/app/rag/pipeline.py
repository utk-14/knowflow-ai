from app.rag.router_agent import route_query
from app.rag.retrieve import retrieve_relevant_chunks
from app.rag.web_search import web_search
from app.rag.generate import generate_answer


MIN_SIMILARITY = 0.28   # tune later after seeing real scores


def run_rag_pipeline(
    user_id: str,
    question: str,
    chat_history: list[dict],
) -> dict:
    """
    Orchestrates the full RAG flow:
      1. Route query (local / web / both)
      2. Retrieve context (with threshold + web fallback)
      3. Generate grounded answer
      4. Return answer + route + sources
    """
    route = route_query(question, chat_history)
    print(f"[pipeline] route={route} for query={question[:80]!r}")

    context_parts: list[str] = []
    sources: list[dict] = []
    local_hits = 0

    # ---- 1. Local retrieval (if route allows) ----
    if route in ("local", "both"):
        chunks = retrieve_relevant_chunks(user_id, question, top_k=5)

        # Apply similarity threshold — reject noise
        chunks = [c for c in chunks if c.get("similarity", 0) >= MIN_SIMILARITY]
        local_hits = len(chunks)

        for c in chunks:
            context_parts.append(f"[From user's document]\n{c['content']}")
            sources.append({
                "type": "document",
                "similarity": round(c["similarity"], 3),
                "preview": c["content"][:150],
            })

    # ---- 2. Web search (if route allows OR local failed) ----
    should_search_web = (
        route == "web"
        or route == "both"
        or (route == "local" and local_hits == 0)
    )

    if should_search_web:
        try:
            results = web_search(question, top_k=3)
            for r in results:
                context_parts.append(
                    f"[From the web: {r['title']}]\n{r['snippet']}\nURL: {r['url']}"
                )
                sources.append({
                    "type": "web",
                    "title": r["title"],
                    "url": r["url"],
                })
        except Exception as e:
            print(f"[pipeline] web search failed: {e}")

    # ---- 3. Build context string ----
    if not context_parts:
        context = "No relevant context was found in the user's documents or the web."
    else:
        context = "\n\n---\n\n".join(context_parts)

    # ---- 4. Generate the answer ----
    answer = generate_answer(question, context, chat_history)

    # ---- 5. Report what actually happened (useful for the frontend) ----
    actual_route = route
    if route == "local" and local_hits == 0 and should_search_web:
        actual_route = "local→web (fallback)"

    return {
        "answer": answer,
        "route": actual_route,
        "sources": sources,
    }