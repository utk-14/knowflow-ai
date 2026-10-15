from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.auth import get_current_user
from app.rag.ingest import ingest_pdf
from app.db import supabase_admin

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    """Upload a PDF and ingest it into the user's private knowledge base."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()

    # Guard against absurdly large uploads on free tier
    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF exceeds 20 MB limit")

    result = ingest_pdf(user_id, file.filename, file_bytes)
    return {"status": "ok", **result}


@router.get("/list")
def list_documents(user_id: str = Depends(get_current_user)):
    """Return the current user's uploaded documents."""
    response = (
        supabase_admin.table("documents")
        .select("id, filename, uploaded_at")
        .eq("user_id", user_id)
        .order("uploaded_at", desc=True)
        .execute()
    )
    return {"documents": response.data or []}


@router.delete("/{document_id}")
def delete_document(document_id: str, user_id: str = Depends(get_current_user)):
    """Delete a document and all its chunks (cascade handles chunks)."""
    response = (
        supabase_admin.table("documents")
        .delete()
        .eq("id", document_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": document_id}