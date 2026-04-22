import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timezone

from app.database import get_db
from app.models import User, Subscription, PlanType, SubStatus
from app.routers.auth import get_current_user_dep
from app.config import settings
from app.services.email import send_payment_failed_email

stripe.api_key = settings.STRIPE_SECRET_KEY
router = APIRouter(prefix="/payments", tags=["payments"])

PRICE_TO_PLAN = {
    settings.STRIPE_PRICE_PRO_MONTHLY: PlanType.pro,
    settings.STRIPE_PRICE_PRO_YEARLY: PlanType.pro,
    settings.STRIPE_PRICE_BUSINESS: PlanType.business,
}


class CheckoutRequest(BaseModel):
    price_id: str  # STRIPE_PRICE_PRO_MONTHLY | STRIPE_PRICE_PRO_YEARLY | STRIPE_PRICE_BUSINESS


@router.post("/checkout")
async def create_checkout(
    body: CheckoutRequest,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    valid_prices = {
        settings.STRIPE_PRICE_PRO_MONTHLY,
        settings.STRIPE_PRICE_PRO_YEARLY,
        settings.STRIPE_PRICE_BUSINESS,
    }
    if body.price_id not in valid_prices:
        raise HTTPException(status_code=400, detail="Plano inválido")

    # Criar ou reutilizar customer Stripe
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, metadata={"user_id": user.id})
        user.stripe_customer_id = customer.id
        await db.commit()

    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": body.price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.APP_URL}/dashboard?payment=success",
        cancel_url=f"{settings.APP_URL}/pricing?payment=canceled",
        allow_promotion_codes=True,
        billing_address_collection="auto",
        tax_id_collection={"enabled": True},  # Para IVA EU
        automatic_tax={"enabled": True},
    )
    return {"checkout_url": session.url}


@router.get("/portal")
async def billing_portal(
    user: User = Depends(get_current_user_dep),
):
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="Sem subscrição ativa")

    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=f"{settings.APP_URL}/dashboard",
    )
    return {"portal_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Webhook inválido")

    et = event["type"]
    data = event["data"]["object"]

    if et in ("customer.subscription.created", "customer.subscription.updated"):
        await _handle_subscription_change(data, db)
    elif et == "customer.subscription.deleted":
        await _handle_subscription_deleted(data, db)
    elif et == "invoice.payment_failed":
        await _handle_payment_failed(data, db)

    return {"received": True}


async def _get_user_by_customer(customer_id: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
    return result.scalar_one_or_none()


async def _handle_subscription_change(sub_data: dict, db: AsyncSession):
    user = await _get_user_by_customer(sub_data["customer"], db)
    if not user:
        return

    price_id = sub_data["items"]["data"][0]["price"]["id"]
    plan = PRICE_TO_PLAN.get(price_id, PlanType.free)
    status_map = {
        "active": SubStatus.active,
        "past_due": SubStatus.past_due,
        "canceled": SubStatus.canceled,
        "trialing": SubStatus.trialing,
    }
    status = status_map.get(sub_data["status"], SubStatus.active)
    period_end = datetime.fromtimestamp(sub_data["current_period_end"], tz=timezone.utc)

    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id).order_by(Subscription.id.desc()))
    sub = result.scalar_one_or_none()
    if sub:
        sub.plan = plan
        sub.status = status
        sub.stripe_subscription_id = sub_data["id"]
        sub.stripe_price_id = price_id
        sub.current_period_end = period_end
    else:
        db.add(Subscription(
            user_id=user.id, plan=plan, status=status,
            stripe_subscription_id=sub_data["id"],
            stripe_price_id=price_id,
            current_period_end=period_end,
        ))
    await db.commit()


async def _handle_subscription_deleted(sub_data: dict, db: AsyncSession):
    user = await _get_user_by_customer(sub_data["customer"], db)
    if not user:
        return
    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id).order_by(Subscription.id.desc()))
    sub = result.scalar_one_or_none()
    if sub:
        sub.status = SubStatus.canceled
        sub.plan = PlanType.free
        await db.commit()


async def _handle_payment_failed(invoice_data: dict, db: AsyncSession):
    user = await _get_user_by_customer(invoice_data["customer"], db)
    if not user:
        return
    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id).order_by(Subscription.id.desc()))
    sub = result.scalar_one_or_none()
    if sub:
        sub.status = SubStatus.past_due
        await db.commit()
    await send_payment_failed_email(user.email)
