import httpx
from app.config import settings


ROUTER_PROMPT = """You are a query classifier for a document-based AI assistant.

The user may have uploaded PDFs. Classify their question into exactly one category:

- "local" → The question is about the user's uploaded documents, files, notes, or private knowledge. Also use "local" when the question is ambiguous.
- "web"   → The question is clearly about current events, weather, news, today's date, live scores, stock prices, or world knowledge the user did not upload.
- "both"  → The question explicitly combines private documents AND external/current information.

Decision rules:
1. If the question contains words like "my document", "the file", "PDF", "my notes", "the contract", "uploaded" → "local"
2. If the question contains words like "weather", "today", "news", "latest", "current", "who won", "price of", "when is" → "web"
3. If the question asks to compare/combine documents with external info → "both"
4. If ambiguous or unclear → "local"

Examples:
- "Summarize my PDF" → local
- "What does the contract say about termination?" → local
- "What is the weather today?" → web
- "Latest news on AI regulation" → web
- "Compare the document's projections to industry trends" → both

Respond with EXACTLY one lowercase word: local, web, or both. No punctuation. No explanation."""


def route_query(question: str, chat_history: list[dict]) -> str:
    """Classify the query as local / web / both. Falls back to local."""
    history_text = ""
    for msg in chat_history[-4:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content'][:200]}\n"

    if history_text:
        user_content = f"Recent conversation:\n{history_text}\nUser's question: {question}"
    else:
        user_content = f"User's question: {question}"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.0,
        "max_tokens": 500,
        "reasoning_format": "hidden",
    }

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[router] Groq error: {e}")
        return "local"

    try:
        content = response.json()["choices"][0]["message"]["content"].strip().lower()
    except (KeyError, IndexError) as e:
        print(f"[router] Parse error: {e}")
        return "local"

    print(f"[router] raw: {content!r} for query: {question[:60]!r}")

    if "both" in content:
        return "both"
    if "web" in content:
        return "web"
    return "local"