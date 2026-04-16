from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

from distraction_blocker import DistractionBlocker
from db import get_blocked_sites, add_blocked_site

app = FastAPI()
blocker = DistractionBlocker()

class CheckRequest(BaseModel):
    url: str
    user_id: str

@app.post("/check-url")

async def check_url(req: CheckRequest):

    # Fetch this user's blocked sites from Supabase
    sites = await get_blocked_sites(req.user_id)  # your Supabase query
    
    blocker.set_blocked_sites(sites)
    
    current_time = datetime.now().strftime("%H:%M")
    try:

        is_blocked = blocker.check_access(req.url, current_time)

        return {"blocked": is_blocked}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/blocked-sites/{user_id}")

async def get_sites(user_id: str):

    return await get_blocked_sites(user_id)

@app.post("/blocked-sites/{user_id}")
async def add_site(user_id: str, url: str):
    # Insert into Supabase blocked_sites table
    await add_blocked_site(user_id, url)
    return {"status": "added"}
...