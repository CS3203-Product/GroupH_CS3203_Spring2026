from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from DistractionBlocker import DistractionBlocker
from db import get_blocked_sites, add_blocked_site, delete_blocked_site

app = FastAPI()

blocker = DistractionBlocker()

class CheckRequest(BaseModel):
    url: str
    user_id: str

@app.post("/blocker/check-url")

async def check_url(req: CheckRequest):
    
    sites = await get_blocked_sites(req.user_id)
    
    blocker.set_blocked_sites(sites)
   
    current_time = datetime.now().strftime("%H:%M")
    try:
       
        is_blocked = blocker.check_access(req.url, current_time)
       
        return {"blocked": is_blocked}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/blocker/sites/{user_id}")

async def get_sites(user_id: str):

    return await get_blocked_sites(user_id)

@app.post("/blocker/sites/{user_id}")

async def add_site(user_id: str, url: str):
    await add_blocked_site(user_id, url)

    return {"added": url}

@app.delete("/blocker/sites/{user_id}/{url}")

async def delete_site(user_id: str, url: str):
    await delete_blocked_site(user_id, url)
    
    return {"deleted": url}