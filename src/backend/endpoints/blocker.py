"""Distraction blocker API: blocked sites in Postgres + JWT auth."""

import logging
from datetime import datetime

from DistractionBlocker import DistractionBlocker
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlmodel import Session

from src.backend.deps import get_user_from_token
from src.core import security
from src.db.session import get_db
from src.repositories.blocked_site import blocked_site_repo
from src.repositories.user import user_repo

logger = logging.getLogger(__name__)

router = APIRouter()
blocker = DistractionBlocker()
http_bearer_optional = HTTPBearer(auto_error=False)


class CheckRequest(BaseModel):
    url: str
    """Deprecated: prefer ``Authorization: Bearer``; retained for local tooling."""

    user_id: str | None = None


class ExtensionLoginBody(BaseModel):
    email: EmailStr
    password: str


def _parse_owner_id(user_id: str) -> int:
    try:
        return int(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid user_id") from e


def _blocked_user_id(
    db: Session,
    credentials: HTTPAuthorizationCredentials | None,
    body_user_id: str | None,
) -> int:
    if credentials:
        user = get_user_from_token(db, credentials.credentials)
        return user.id
    if body_user_id:
        return _parse_owner_id(body_user_id)
    raise HTTPException(status_code=401, detail="Missing bearer token or user_id")


@router.post("/blocker/auth/login")
def extension_login(body: ExtensionLoginBody, db: Session = Depends(get_db)) -> dict:
    """JSON login for the browser extension; returns JWT and stable user id for storage."""
    user = user_repo.authenticate(db=db, email=str(body.email), password=body.password)
    return {
        "access_token": security.create_access_token(user.id),
        "token_type": "bearer",
        "user_id": user.id,
    }


@router.get("/blocker/blocked-urls")
def get_blocked_urls(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> dict:
    """Return all blocked hostnames for the authenticated user."""
    user = get_user_from_token(db, credentials.credentials)
    urls = blocked_site_repo.list_urls(db, owner_id=user.id)
    return {"urls": urls}


@router.post("/blocker/check-url")
def check_url(
    req: CheckRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer_optional),
):
    owner_id = _blocked_user_id(db, credentials, req.user_id)
    user = user_repo.get(db, owner_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    sites = blocked_site_repo.list_urls(db, owner_id=owner_id)
    logger.debug("check-url sites owner_id=%s sites=%s", owner_id, sites)
    print("check-url sites owner_id=%s sites=%s", owner_id, sites)
    blocker.set_blocked_sites(sites)
    current_time = datetime.now().strftime("%H:%M")
    logger.debug(
        "check-url owner_id=%s url=%s current_time=%s user_db=%s blocked_urls=%s",
        owner_id,
        req.url,
        current_time,
        {
            "id": user.id,
            "email": user.email,
            "distraction_block_start": user.distraction_block_start,
            "distraction_block_end": user.distraction_block_end,
        },
        sites,
    )
    try:
        is_blocked = blocker.check_access(
            req.url,
            current_time,
            window_start=user.distraction_block_start,
            window_end=user.distraction_block_end,
        )
        return {"blocked": is_blocked}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/blocker/sites/{user_id}")
def get_sites(user_id: str, db: Session = Depends(get_db)):
    return blocked_site_repo.list_urls(db, owner_id=_parse_owner_id(user_id))


@router.post("/blocker/sites/{user_id}")
def add_site(user_id: str, url: str, db: Session = Depends(get_db)):
    blocked_site_repo.add(db, owner_id=_parse_owner_id(user_id), url=url)
    return {"added": url}


@router.delete("/blocker/sites/{user_id}/{url:path}")
def delete_site(user_id: str, url: str, db: Session = Depends(get_db)):
    blocked_site_repo.delete(db, owner_id=_parse_owner_id(user_id), url=url)
    return {"deleted": url}
