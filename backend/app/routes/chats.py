from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import get_current_user
from app.db import supabase_admin
from app.rag.pipeline import run_rag_pipeline

router = APIRouter(prefix="/chats", tags=["chats"])


class NewChatRequest(BaseModel):
    title: str | None = None


class MessageRequest(BaseModel):
    message: str


# ---------- Create a new chat ----------
@router.post("")
def create_chat(
    body: NewChatRequest,
    user_id: str = Depends(get_current_user),
):
    response = supabase_admin.table("chats").insert({
        "user_id": user_id,
        "title": body.title or "New Chat",
    }).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create chat")

    return {"chat": response.data[0]}


# ---------- List all chats for the user ----------
@router.get("")
def list_chats(user_id: str = Depends(get_current_user)):
    response = (
        supabase_admin.table("chats")
        .select("id, title, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"chats": response.data or []}


# ---------- Load messages of a chat ----------
@router.get("/{chat_id}/messages")
def get_messages(chat_id: str, user_id: str = Depends(get_current_user)):
    chat = (
        supabase_admin.table("chats")
        .select("id")
        .eq("id", chat_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not chat.data:
        raise HTTPException(status_code=404, detail="Chat not found")

    msgs = (
        supabase_admin.table("messages")
        .select("id, role, content, created_at")
        .eq("chat_id", chat_id)
        .order("created_at", desc=False)
        .execute()
    )
    return {"messages": msgs.data or []}


# ---------- Send a message (main RAG endpoint) ----------
@router.post("/{chat_id}/messages")
def send_message(
    chat_id: str,
    body: MessageRequest,
    user_id: str = Depends(get_current_user),
):
    # 1. Verify chat ownership
    chat = (
        supabase_admin.table("chats")
        .select("id, title")
        .eq("id", chat_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not chat.data:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 2. Load chat history
    history_resp = (
        supabase_admin.table("messages")
        .select("role, content")
        .eq("chat_id", chat_id)
        .order("created_at", desc=False)
        .execute()
    )
    history = history_resp.data or []

    # 3. Save user message
    supabase_admin.table("messages").insert({
        "chat_id": chat_id,
        "role": "user",
        "content": body.message,
    }).execute()

    # 4. Run RAG pipeline
    result = run_rag_pipeline(
        user_id=user_id,
        question=body.message,
        chat_history=history,
    )

    # 5. Save assistant reply
    supabase_admin.table("messages").insert({
        "chat_id": chat_id,
        "role": "assistant",
        "content": result["answer"],
    }).execute()

    # 6. Auto-title on first message
    if not history:
        title = body.message[:50] + ("..." if len(body.message) > 50 else "")
        supabase_admin.table("chats").update({"title": title}).eq("id", chat_id).execute()

    return {
        "reply": result["answer"],
        "route": result["route"],
        "sources": result["sources"],
    }