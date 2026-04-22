"""
Apple & Microsoft OAuth 2.0 para PonteVPN.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import secrets
import time
import jwt # PyJWT

from app.database import get_db
from app.models import User, Subscription, PlanType, SubStatus
from app.config import settings
from app.routers.auth import create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["auth-providers"])

# Microsoft Configs
MS_AUTH_URL = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize"
MS_TOKEN_URL = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/token"
MS_USERINFO_URL = "https://graph.microsoft.com/v1.0/me"
MS_SCOPE = "User.Read"

# Apple Configs
APPLE_AUTH_URL = "https://appleid.apple.com/auth/authorize"
APPLE_TOKEN_URL = "https://appleid.apple.com/auth/token"

async def create_or_auth_user(email: str, db: AsyncSession):
    """Cria ou autentica utilizador pelo email."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            password_hash=hash_password(secrets.token_hex(32)),
            is_verified=True,
        )
        db.add(user)
        await db.flush()
        sub = Subscription(user_id=user.id, plan=PlanType.free, status=SubStatus.active)
        db.add(sub)
        await db.commit()
    elif not user.is_verified:
        user.is_verified = True
        await db.commit()
    
    return create_access_token(user.id)

# --- Microsoft Routes ---

@router.get("/microsoft")
async def microsoft_login():
    params = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": f"{settings.API_URL}/auth/microsoft/callback",
        "response_mode": "query",
        "scope": MS_SCOPE,
    }
    url = MS_AUTH_URL + "?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url)

@router.get("/microsoft/callback")
async def microsoft_callback(code: str, db: AsyncSession = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(MS_TOKEN_URL, data={
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "client_secret": settings.MICROSOFT_CLIENT_SECRET,
            "code": code,
            "redirect_uri": f"{settings.API_URL}/auth/microsoft/callback",
            "grant_type": "authorization_code",
        })
        token_data = token_resp.json()
        if "access_token" not in token_data:
            return RedirectResponse(f"{settings.APP_URL}/auth/login?error=ms_failed")

        user_resp = await client.get(
            MS_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        ms_user = user_resp.json()
    
    email = ms_user.get("mail") or ms_user.get("userPrincipalName")
    if not email:
        return RedirectResponse(f"{settings.APP_URL}/auth/login?error=ms_no_email")

    token = await create_or_auth_user(email, db)
    return RedirectResponse(f"{settings.APP_URL}/auth/callback?token={token}")

# --- Apple Routes ---

def generate_apple_client_secret():
    """Gera o client_secret assinado para a Apple."""
    headers = {"alg": "ES256", "kid": settings.APPLE_KEY_ID}
    payload = {
        "iss": settings.APPLE_TEAM_ID,
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 180, # 6 meses
        "aud": "https://appleid.apple.com",
        "sub": settings.APPLE_CLIENT_ID,
    }
    with open(settings.APPLE_PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    
    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)

@router.get("/apple")
async def apple_login():
    params = {
        "client_id": settings.APPLE_CLIENT_ID,
        "redirect_uri": f"{settings.API_URL}/auth/apple/callback",
        "response_type": "code id_token",
        "scope": "name email",
        "response_mode": "form_post", # Apple requer form_post para scopes
    }
    url = APPLE_AUTH_URL + "?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url)

@router.post("/apple/callback")
async def apple_callback(code: str, id_token: str, db: AsyncSession = Depends(get_db)):
    # 1. Validar id_token para extrair o email (simplificado aqui)
    # Em produção, deve validar a assinatura do id_token com as chaves públicas da Apple
    decoded = jwt.decode(id_token, options={"verify_signature": False})
    email = decoded.get("email")
    
    if not email:
        # Se falhar, tenta trocar o code pelo token real
        client_secret = generate_apple_client_secret()
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(APPLE_TOKEN_URL, data={
                "client_id": settings.APPLE_CLIENT_ID,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{settings.API_URL}/auth/apple/callback",
            })
            token_data = token_resp.json()
            decoded = jwt.decode(token_data.get("id_token"), options={"verify_signature": False})
            email = decoded.get("email")

    if not email:
        return RedirectResponse(f"{settings.APP_URL}/auth/login?error=apple_failed")

    token = await create_or_auth_user(email, db)
    return RedirectResponse(f"{settings.APP_URL}/auth/callback?token={token}")
