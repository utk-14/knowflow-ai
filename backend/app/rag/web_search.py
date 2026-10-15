import httpx
from fastapi import HTTPException
from app.config import settings


def web_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Query LangSearch and return a list of {title, url, snippet} dicts.
    Returns [] if no results or on error.
    """
    if not query.strip():
        return []

    url = "https://api.langsearch.com/v1/web-search"
    headers = {
        "Authorization": f"Bearer {settings.LANGSEARCH_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": query,
        "freshness": "noLimit",
        "summary": True,
        "count": top_k,
    }

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"LangSearch failed: {e.response.status_code} {e.response.text}",
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"LangSearch error: {str(e)}")

    data = response.json()

    # LangSearch response shape: { data: { webPages: { value: [...] } } }
    pages = (
        data.get("data", {})
            .get("webPages", {})
            .get("value", [])
    )

    results = []
    for page in pages[:top_k]:
        results.append({
            "title": page.get("name", ""),
            "url": page.get("url", ""),
            "snippet": page.get("summary") or page.get("snippet", ""),
        })
    return results