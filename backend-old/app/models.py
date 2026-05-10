from sqlalchemy import String, Boolean, Integer, BigInteger, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class PlanType(str, enum.Enum):
    free = "free"
    pro = "pro"
    business = "business"


class SubStatus(str, enum.Enum):
    active = "active"
    past_due = "past_due"
    canceled = "canceled"
    trialing = "trialing"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verify_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
    vpn_configs: Mapped[list["VPNConfig"]] = relationship(back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    plan: Mapped[PlanType] = mapped_column(SAEnum(PlanType), default=PlanType.free)
    status: Mapped[SubStatus] = mapped_column(SAEnum(SubStatus), default=SubStatus.active)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    bandwidth_used_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="subscriptions")


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    country_code: Mapped[str] = mapped_column(String(5), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    ip: Mapped[str] = mapped_column(String(50), nullable=False)
    wg_port: Mapped[int] = mapped_column(Integer, default=51820)
    wg_public_key: Mapped[str] = mapped_column(String(255), nullable=False)
    agent_url: Mapped[str] = mapped_column(String(255), nullable=False)  # URL do agente WireGuard
    agent_secret: Mapped[str] = mapped_column(String(255), nullable=True) # Secret para autenticação
    capacity: Mapped[int] = mapped_column(Integer, default=500)
    active_peers: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Plano mínimo para acesso (free = todos, pro = pro+business)
    min_plan: Mapped[PlanType] = mapped_column(SAEnum(PlanType), default=PlanType.free)

    vpn_configs: Mapped[list["VPNConfig"]] = relationship(back_populates="server")


class VPNConfig(Base):
    __tablename__ = "vpn_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"), nullable=False)
    # Somente a chave pública é armazenada — a privada é gerada e entregue ao usuário imediatamente
    wg_public_key: Mapped[str] = mapped_column(String(255), nullable=False)
    vpn_ip: Mapped[str] = mapped_column(String(50), nullable=False)  # IP do peer na rede VPN
    device_name: Mapped[str] = mapped_column(String(100), default="Meu Dispositivo")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="vpn_configs")
    server: Mapped["Server"] = relationship(back_populates="vpn_configs")
