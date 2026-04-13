"""Auth routes — PRJ0-28.

POST /register  — create account
POST /login     — get access token + httpOnly refresh cookie
POST /refresh   — rotate refresh token
POST /logout    — revoke all tokens, clear cookie
GET  /me        — current user profile
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token
from app.core.auth_deps import get_current_user
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, UserRead, TokenResponse
from app.services import auth_service as svc

router = APIRouter()

_COOKIE = "refresh_token"
_COOKIE_PATH = "/api/v1/auth/refresh"


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        path=_COOKIE_PATH,
        max_age=7 * 24 * 3600,
        secure=False,  # set True in prod with HTTPS
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=_COOKIE, path=_COOKIE_PATH)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await svc.register_user(db, data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    user = await svc.authenticate_user(db, data.email, data.password)
    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role},
        settings.jwt_secret_key,
        settings.jwt_algorithm,
        settings.access_token_expire_minutes,
    )
    raw_refresh = create_refresh_token()
    await svc.create_session(db, user.id, raw_refresh)
    _set_refresh_cookie(response, raw_refresh)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    raw_token = request.cookies.get(_COOKIE)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    settings = get_settings()
    user, new_raw = await svc.rotate_refresh_token(db, raw_token)
    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role},
        settings.jwt_secret_key,
        settings.jwt_algorithm,
        settings.access_token_expire_minutes,
    )
    _set_refresh_cookie(response, new_raw)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await svc.revoke_all_user_tokens(db, current_user.id)
    _clear_refresh_cookie(response)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
