"""
Google OAuth 2.0 para PonteVPN.
Requer: GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET no .env
"""
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import secrets

from app.database import get_db
from app.models import User, Subscription, PlanType, SubStatus
from app.config import settings
from app.routers.auth import create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["auth-google"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPE = "openid email profile"


@router.get("/google")
async def google_login():
    """Redireciona o utilizador para o ecrã de consentimento do Google."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.API_URL}/auth/google/callback",
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "select_account",
    }
    url = GOOGLE_AUTH_URL + "?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Recebe o código do Google, troca por token, cria/autentica utilizador."""

    # 1. Trocar código por access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": f"{settings.API_URL}/auth/google/callback",
            "grant_type": "authorization_code",
        })
        token_data = token_resp.json()

        # 2. Buscar informações do utilizador
        user_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        google_user = user_resp.json()

    email = google_user.get("email")
    if not email:
        return RedirectResponse(f"{settings.APP_URL}/auth/login?error=google_failed")

    # 3. Criar ou encontrar utilizador
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            password_hash=hash_password(secrets.token_hex(32)),  # password aleatória, não usada
            is_verified=True,  # Google já verificou o email
        )
        db.add(user)
        await db.flush()
        sub = Subscription(user_id=user.id, plan=PlanType.free, status=SubStatus.active)
        db.add(sub)
        await db.commit()
    elif not user.is_verified:
        user.is_verified = True
        await db.commit()

    # 4. Gerar JWT e redirecionar para o dashboard
    token = create_access_token(user.id)
    return RedirectResponse(f"{settings.APP_URL}/auth/callback?token={token}")
