from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import secrets

from app.database import get_db
from app.models import User, Subscription, PlanType, SubStatus
from app.config import settings
from app.services.email import send_verification_email, send_welcome_email

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Schemas ──────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    is_verified: bool
    plan: str


# ── Helpers ──────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.SECRET_KEY, settings.ALGORITHM)


async def get_current_user(token: str = Depends(lambda: None), db: AsyncSession = Depends(get_db)):
    """Dependency: extrai e valida JWT, retorna User."""
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    raise NotImplementedError  # implementado via get_current_user_dep abaixo


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user_dep(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilizador não encontrado")
    return user


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email já registado")

    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="A password deve ter pelo menos 8 caracteres")

    verify_token = secrets.token_urlsafe(32)
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        verify_token=verify_token,
    )
    db.add(user)
    await db.flush()

    # Criar subscrição gratuita por defeito
    sub = Subscription(user_id=user.id, plan=PlanType.free, status=SubStatus.active)
    db.add(sub)
    await db.commit()

    await send_verification_email(body.email, verify_token)
    return {"message": "Conta criada. Verifique o seu email."}


@router.get("/verify")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.verify_token == token))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    user.is_verified = True
    user.verify_token = None
    await db.commit()
    await send_welcome_email(user.email)
    return {"message": "Email confirmado com sucesso"}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Confirme o seu email antes de entrar")

    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user_dep), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
        .order_by(Subscription.id.desc())
    )
    sub = result.scalar_one_or_none()
    plan = sub.plan.value if sub else "free"
    return UserOut(id=user.id, email=user.email, is_verified=user.is_verified, plan=plan)
