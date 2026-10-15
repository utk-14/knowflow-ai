from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.auth import get_current_user
from app.db import supabase_admin
from app.routes import documents, chats

app = FastAPI(title="KnowFlow AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chats.router)

@app.get("/")
def root():
    return {"status": "ok", "service": "KnowFlow AI"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/me")
def me(user_id: str = Depends(get_current_user)):
    result = supabase_admin.auth.admin.get_user_by_id(user_id)
    return {
        "user_id": user_id,
        "email": result.user.email if result.user else None
    }