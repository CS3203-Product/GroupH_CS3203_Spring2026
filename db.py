from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


async def get_blocked_sites(user_id: str):
    response = supabase.table("blocked_sites").select("url").eq("user_id", user_id).execute()
    return [row["url"] for row in response.data]


async def add_blocked_site(user_id: str, url: str):
    supabase.table("blocked_sites").insert({"user_id": user_id, "url": url}).execute()


async def delete_blocked_site(user_id: str, url: str):
    supabase.table("blocked_sites").delete().eq("user_id", user_id).eq("url", url).execute()