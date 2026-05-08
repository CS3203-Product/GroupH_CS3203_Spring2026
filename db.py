from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_KEY = os.getenv("SECRET_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

#CWE-703: Supabase call may fail due to network issues or invalid credentials.
# Always handle APIError to prevent unhandled exception crashing the server
async def get_blocked_sites(user_id: str):
    response = supabase.table("blocked_sites").select("url").eq("user_id", user_id).execute()
    return [row["url"] for row in response.data]

# Insert may fail if Supabase is unreachable or RLS policy blocks the request
async def add_blocked_site(user_id: str, url: str):
    supabase.table("blocked_sites").insert({"user_id": user_id, "url": url}).execute()

#CWE-703: Delete silent fails if row doesn't exist. Handle to avoid misleading responses.
async def delete_blocked_site(user_id: str, url: str):
    supabase.table("blocked_sites").delete().eq("user_id", user_id).eq("url", url).execute()
