import io
import httpx
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastapi import HTTPException
from app.config import settings
from app.db import supabase_admin


# ---- 1. Extract text from PDF bytes ----
def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Read a PDF from memory and return concatenated text from all pages.
    Raises 400 if the PDF is unreadable or has no extractable text.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read PDF: {str(e)}")

    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages_text.append(text)

    full_text = "\n\n".join(pages_text).strip()

    if not full_text:
        raise HTTPException(
            status_code=400,
            detail="PDF contains no extractable text (may be scanned/image-only)",
        )
    return full_text


# ---- 2. Split text into overlapping chunks ----
def chunk_text(text: str, chunk_size: int = 700, chunk_overlap: int = 150) -> list[str]:
    """
    Split raw text into semantically meaningful chunks.
    Uses paragraph -> sentence -> word fallback ordering.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    return [c.strip() for c in splitter.split_text(text) if c.strip()]


# ---- 3. Embed chunks via Jina AI ----
def embed_texts(texts: list[str], task: str = "retrieval.passage") -> list[list[float]]:
    """
    Call Jina AI embeddings API. Returns a list of 1024-dim vectors.
    `task` should be:
      - "retrieval.passage" for documents being indexed
      - "retrieval.query"   for user queries at search time
    """
    if not texts:
        return []

    url = "https://api.jina.ai/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {settings.JINA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "jina-embeddings-v3",
        "task": task,
        "dimensions": 1024,
        "input": texts,
    }

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Jina embedding failed: {e.response.status_code} {e.response.text}",
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Jina request error: {str(e)}")

    data = response.json()
    # Jina returns { data: [ { embedding: [...], index: 0 }, ... ] }
    return [item["embedding"] for item in data["data"]]


# ---- 4. Full pipeline: bytes -> DB rows ----
def ingest_pdf(user_id: str, filename: str, file_bytes: bytes) -> dict:
    """
    End-to-end ingestion:
      1. Extract text
      2. Create a `documents` row
      3. Chunk text
      4. Embed chunks
      5. Insert chunks (content + embedding) into `chunks` table
    Returns a summary dict.
    """
    # 1. Extract
    text = extract_text_from_pdf(file_bytes)

    # 2. Insert document record first (so we get an id for the chunks)
    doc_response = supabase_admin.table("documents").insert({
        "user_id": user_id,
        "filename": filename,
    }).execute()

    if not doc_response.data:
        raise HTTPException(status_code=500, detail="Failed to create document record")

    document_id = doc_response.data[0]["id"]

    # 3. Chunk
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks produced from PDF")

    # 4. Embed in batches (Jina supports up to 100 inputs per call)
    all_embeddings: list[list[float]] = []
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        all_embeddings.extend(embed_texts(batch, task="retrieval.passage"))

    if len(all_embeddings) != len(chunks):
        raise HTTPException(
            status_code=500,
            detail=f"Embedding count mismatch: {len(all_embeddings)} vs {len(chunks)}",
        )

    # 5. Insert into Supabase
    rows = [
        {
            "document_id": document_id,
            "user_id": user_id,
            "content": chunk,
            "embedding": embedding,
        }
        for chunk, embedding in zip(chunks, all_embeddings)
    ]

    # Supabase has a payload limit; insert in batches too
    for i in range(0, len(rows), batch_size):
        supabase_admin.table("chunks").insert(rows[i : i + batch_size]).execute()

    return {
        "document_id": document_id,
        "filename": filename,
        "characters": len(text),
        "chunks": len(chunks),
    }