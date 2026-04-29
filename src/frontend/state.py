from typing import TypedDict
from nicegui import app
from jose import jwt, JWTError
from src.core.config import settings
from src.core.security import ALGORITHM



class AuthState(TypedDict):
    """
    Defines the structure of the authentication data stored in the session.
    """

    access_token: str
    token_type: str

def get_auth() -> AuthState | None:
    """
    Retrieves authentication data from session storage.
    If the token is expired or invalid, clear auth and return None.
    """
    auth = app.storage.user.get("auth")

    if not auth:
        return None

    token = auth.get("access_token")

    try:
        jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        clear_auth()
        return None

    return auth


def set_auth(auth: AuthState) -> None:
    """
    Saves the authentication data to the session storage after a successful login.
    """
    app.storage.user["auth"] = auth


def clear_auth() -> None:
    """
    Removes authentication data from the session upon logout.
    """
    app.storage.user.pop("auth", None)


def get_token() -> str | None:
    """
    Formats the stored token for use in API request headers.
    Returns the token string (e.g., "Bearer a1b2c3d4...") or None.
    """
    auth = get_auth()
    return f"{auth['token_type']} {auth['access_token']}" if auth else None
