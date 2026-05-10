from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.models import Server, PlanType
from app.routers.auth import get_current_user_dep
from app.models import User, Subscription

router = APIRouter(prefix="/servers", tags=["servers"])

FLAG_EMOJIS = {
    "BR": "🇧🇷", "DE": "🇩🇪", "NL": "🇳🇱", "US": "🇺🇸",
    "GB": "🇬🇧", "FR": "🇫🇷", "PT": "🇵🇹", "JP": "🇯🇵",
}


class ServerOut(BaseModel):
    id: int
    name: str
    country: str
    country_code: str
    city: str
    flag: str
    is_available: bool  # False se o plano do user não permite
    load_percent: int


@router.get("", response_model=list[ServerOut])
async def list_servers(
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    # Buscar plano do utilizador
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
        .order_by(Subscription.id.desc())
    )
    sub = result.scalar_one_or_none()
    user_plan = sub.plan if sub else PlanType.free

    result = await db.execute(select(Server).where(Server.is_active == True))
    servers = result.scalars().all()

    plan_order = {PlanType.free: 0, PlanType.pro: 1, PlanType.business: 2}

    return [
        ServerOut(
            id=s.id,
            name=s.name,
            country=s.country,
            country_code=s.country_code,
            city=s.city,
            flag=FLAG_EMOJIS.get(s.country_code, "🌐"),
            is_available=plan_order[user_plan] >= plan_order[s.min_plan],
            load_percent=min(100, int(s.active_peers / s.capacity * 100)),
        )
        for s in servers
    ]
