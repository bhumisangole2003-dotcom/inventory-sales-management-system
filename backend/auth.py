import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import models
from database import get_db

bearer = HTTPBearer(auto_error=False)
SESSION_HOURS = 8


def hash_password(password: str) -> str:
    """Salted PBKDF2 hash (built into Python, nothing extra to install)."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split("$")
    new_digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return hmac.compare_digest(new_digest, digest)


def issue_token(db: Session, user: models.User) -> str:
    token = secrets.token_hex(32)
    db.add(models.AuthToken(token=token, user_id=user.id))
    db.commit()
    return token


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> models.User:
    """Use as a dependency on any route that needs a logged-in user."""
    if creds is None:
        raise HTTPException(401, "Please log in")
    session = db.query(models.AuthToken).filter(models.AuthToken.token == creds.credentials).first()
    if not session or datetime.now() - session.created_at > timedelta(hours=SESSION_HOURS):
        raise HTTPException(401, "Session expired, please log in again")
    return session.user
