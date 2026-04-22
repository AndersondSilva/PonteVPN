from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Server, VPNConfig, Subscription, PlanType, SubStatus
from app.routers.auth import get_current_user_dep
from app.services.wireguard import (
    generate_keypair, build_client_config, ip_from_index,
    register_peer_on_server, remove_peer_from_server
)

router = APIRouter(prefix="/vpn", tags=["vpn"])

PLAN_MAX_CONFIGS = {PlanType.free: 1, PlanType.pro: 5, PlanType.business: 20}


class GenerateConfigRequest(BaseModel):
    server_id: int
    device_name: str = "Meu Dispositivo"


class ConfigOut(BaseModel):
    id: int
    server_name: str
    server_country: str
    country_code: str
    device_name: str
    vpn_ip: str
    is_active: bool


@router.get("/configs", response_model=list[ConfigOut])
async def list_configs(
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VPNConfig, Server)
        .join(Server, VPNConfig.server_id == Server.id)
        .where(VPNConfig.user_id == user.id, VPNConfig.is_active == True)
    )
    rows = result.all()
    return [
        ConfigOut(
            id=cfg.id,
            server_name=srv.name,
            server_country=srv.country,
            country_code=srv.country_code,
            device_name=cfg.device_name,
            vpn_ip=cfg.vpn_ip,
            is_active=cfg.is_active,
        )
        for cfg, srv in rows
    ]


@router.post("/generate")
async def generate_config(
    body: GenerateConfigRequest,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    # Verificar plano e limites
    sub_result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
        .order_by(Subscription.id.desc())
    )
    sub = sub_result.scalar_one_or_none()
    user_plan = sub.plan if sub else PlanType.free

    if sub and sub.status not in (SubStatus.active, SubStatus.trialing):
        raise HTTPException(status_code=403, detail="Subscrição inativa. Atualize o pagamento.")

    config_count_result = await db.execute(
        select(func.count()).where(VPNConfig.user_id == user.id, VPNConfig.is_active == True)
    )
    config_count = config_count_result.scalar()
    if config_count >= PLAN_MAX_CONFIGS[user_plan]:
        raise HTTPException(
            status_code=403,
            detail=f"Limite de {PLAN_MAX_CONFIGS[user_plan]} configurações para o plano {user_plan.value}. Faça upgrade."
        )

    # Buscar servidor
    srv_result = await db.execute(select(Server).where(Server.id == body.server_id, Server.is_active == True))
    server = srv_result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")

    # Verificar acesso ao servidor pelo plano
    plan_order = {PlanType.free: 0, PlanType.pro: 1, PlanType.business: 2}
    if plan_order[user_plan] < plan_order[server.min_plan]:
        raise HTTPException(status_code=403, detail="Faça upgrade para aceder a este servidor.")

    # Gerar índice único para o IP do peer (total de peers já criados + 1)
    total_result = await db.execute(select(func.count()).select_from(VPNConfig))
    peer_index = (total_result.scalar() or 0) + 1
    vpn_ip = ip_from_index(peer_index)

    # Gerar chaves — a privada NÃO é armazenada
    private_key, public_key = generate_keypair()

    # Registar peer no servidor VPN
    success = await register_peer_on_server(server.agent_url, public_key, vpn_ip)
    if not success:
        raise HTTPException(status_code=503, detail="Erro ao registar no servidor VPN. Tente novamente.")

    # Persistir apenas a chave pública
    config = VPNConfig(
        user_id=user.id,
        server_id=server.id,
        wg_public_key=public_key,
        vpn_ip=vpn_ip,
        device_name=body.device_name,
    )
    db.add(config)
    server.active_peers += 1
    await db.commit()

    # Montar e retornar o ficheiro .conf (privada está aqui e é descartada após envio)
    conf_content = build_client_config(
        private_key=private_key,
        client_vpn_ip=vpn_ip,
        server_public_key=server.wg_public_key,
        server_endpoint=server.ip,
        server_port=server.wg_port,
    )

    from fastapi.responses import Response
    filename = f"pontevpn-{server.country_code.lower()}-{body.device_name.replace(' ', '_').lower()}.conf"
    return Response(
        content=conf_content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/configs/{config_id}")
async def revoke_config(
    config_id: int,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VPNConfig, Server)
        .join(Server)
        .where(VPNConfig.id == config_id, VPNConfig.user_id == user.id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

    cfg, srv = row
    await remove_peer_from_server(srv.agent_url, cfg.wg_public_key)
    cfg.is_active = False
    srv.active_peers = max(0, srv.active_peers - 1)
    await db.commit()
    return {"message": "Configuração revogada"}
