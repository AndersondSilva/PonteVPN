from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routers import auth, servers, vpn, payments, auth_google, feedback, auth_providers
from app.database import engine, Base

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="PonteVPN API",
    version="1.0.0",
    docs_url="/docs" if True else None,  # Desabilitar em produção se preferir
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pontevpn.com",
        "https://www.pontevpn.com",
        "http://localhost:3000",  # Dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(auth_google.router)
app.include_router(auth_providers.router)
app.include_router(servers.router)
app.include_router(vpn.router)
app.include_router(payments.router)
app.include_router(feedback.router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "PonteVPN API"}
