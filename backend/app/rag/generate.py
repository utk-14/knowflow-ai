import httpx
from fastapi import HTTPException
from app.config import settings


SYSTEM_PROMPT = """You are KnowFlow AI, a helpful assistant.

Answer the user's question using ONLY the provided context.

Rules:
- If the context does not contain the answer, say: "I don't have enough information to answer that."
- Do not make up facts. Do not use your own training knowledge.
- Cite sources when relevant (e.g., "According to the document..." or the URL).
- Be concise. Match the user's tone.
- Use the conversation history to resolve pronouns and follow-ups.
"""


def generate_answer(
    question: str,
    context: str,
    chat_history: list[dict],
) -> str:
    """
    Call Groq to produce the final answer, grounded in `context`.
    `chat_history` is passed for conversation memory.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add chat history (last 6 turns to keep tokens cheap)
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current question with context
    user_content = (
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )
    messages.append({"role": "user", "content": user_content})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
         # In generate_answer():
        "model": "openai/gpt-oss-120b",   # was gpt-oss-120b / llama-3.3-70b

        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Groq generation failed: {e.response.status_code} {e.response.text}",
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Groq error: {str(e)}")

    return response.json()["choices"][0]["message"]["content"].strip()