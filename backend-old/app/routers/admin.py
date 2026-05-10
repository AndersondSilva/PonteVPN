from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import User, Server, VPNConfig, Subscription, PlanType
from app.routers.auth import get_current_user_dep

router = APIRouter(prefix="/admin", tags=["admin"])

async def check_admin(user: User = Depends(get_current_user_dep)):
    # Simulação de check admin (pode ser um campo no DB)
    if not user.email.endswith("@pontevpn.com") and user.id != 1:
        raise HTTPException(status_code=403, detail="Apenas administradores podem acessar.")
    return user

@router.get("/stats", dependencies=[Depends(check_admin)])
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    total_users = await db.execute(select(func.count()).select_from(User))
    total_configs = await db.execute(select(func.count()).select_from(VPNConfig))
    total_servers = await db.execute(select(func.count()).select_from(Server))
    
    # Revenue estimation
    pro_users = await db.execute(select(func.count()).select_from(Subscription).where(Subscription.plan == PlanType.pro))
    biz_users = await db.execute(select(func.count()).select_from(Subscription).where(Subscription.plan == PlanType.business))
    
    mrr = (pro_users.scalar() or 0) * 19 + (biz_users.scalar() or 0) * 199
    
    return {
        "users": total_users.scalar(),
        "configs": total_configs.scalar(),
        "servers": total_servers.scalar(),
        "mrr_estimate": f"R$ {mrr}",
    }

@router.get("/servers", dependencies=[Depends(check_admin)])
async def list_servers_admin(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server))
    return result.scalars().all()
