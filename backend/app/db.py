from supabase import create_client, Client
from app.config import settings

# Backend client — uses SECRET key, bypasses RLS
# Used for writing chunks, saving messages, admin operations
supabase_admin: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SECRET_KEY
)

# Public client — uses PUBLISHABLE key, respects RLS
# Used when acting as a specific user (rare in backend, mostly frontend)
supabase_public: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_PUBLISHABLE_KEY
)