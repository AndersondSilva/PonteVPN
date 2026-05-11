use axum::{
    extract::{State, Json},
    http::StatusCode,
    response::IntoResponse,
};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use crate::models::{User, Subscription, PlanType, SubStatus};
use crate::middleware::auth::ClaimsExtractor;
use stripe::{Client, CheckoutSession, CheckoutSessionMode, CheckoutSessionLineItem, CreateCustomer, CreateCheckoutSession, CreateCheckoutSessionLineItems, CreateBillingPortalSession};
use chrono::{Utc, TimeZone};

#[derive(Deserialize)]
pub struct CheckoutRequest {
    pub price_id: String,
    pub billing_cycle: String, // "monthly", "quarterly", "yearly"
    pub currency: String,      // "BRL", "EUR"
}

#[derive(Serialize)]
pub struct CheckoutResponse {
    pub checkout_url: String,
}

#[derive(Deserialize)]
pub struct PixRequest {
    pub plan_type: PlanType,
}

pub async fn create_checkout(
    State(pool): State<PgPool>,
    ClaimsExtractor(claims): ClaimsExtractor,
    Json(payload): Json<CheckoutRequest>,
) -> impl IntoResponse {
    let user_id: i32 = claims.sub.parse().unwrap();
    let stripe_secret = std::env::var("STRIPE_SECRET_KEY").unwrap_or_default();
    let stripe_client = Client::new(stripe_secret);

    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", user_id)
        .fetch_one(&pool)
        .await
        .unwrap();

    let customer_id = match user.stripe_customer_id {
        Some(id) => id,
        None => {
            let customer_params = CreateCustomer {
                email: Some(&user.email),
                ..Default::default()
            };
            let customer = stripe::Customer::create(&stripe_client, customer_params).await.unwrap();
            sqlx::query!("UPDATE users SET stripe_customer_id = $1 WHERE id = $2", customer.id.to_string(), user_id)
                .execute(&pool)
                .await
                .unwrap();
            customer.id.to_string()
        }
    };

    let app_url = std::env::var("APP_URL").unwrap_or_default();
    
    let mut checkout_params = CreateCheckoutSession::new();
    checkout_params.customer = Some(stripe::CustomerId::from_explicit_id(customer_id));
    
    let mut payment_methods = vec![stripe::CheckoutSessionPaymentMethodType::Card];
    if payload.currency == "EUR" {
        payment_methods.push(stripe::CheckoutSessionPaymentMethodType::SepaDebit);
    }
    
    checkout_params.payment_method_types = Some(payment_methods);
    checkout_params.mode = Some(CheckoutSessionMode::Subscription);
    checkout_params.success_url = Some(&format!("{}/dashboard?payment=success", app_url));
    checkout_params.cancel_url = Some(&format!("{}/pricing?payment=canceled", app_url));
    
    checkout_params.line_items = Some(vec![CreateCheckoutSessionLineItems {
        price: Some(payload.price_id),
        quantity: Some(1),
        ..Default::default()
    }]);

    let session = CheckoutSession::create(&stripe_client, checkout_params).await.unwrap();
    
    Json(CheckoutResponse {
        checkout_url: session.url.unwrap_or_default(),
    })
}

pub async fn billing_portal(
    State(pool): State<PgPool>,
    ClaimsExtractor(claims): ClaimsExtractor,
) -> impl IntoResponse {
    let user_id: i32 = claims.sub.parse().unwrap();
    let stripe_secret = std::env::var("STRIPE_SECRET_KEY").unwrap_or_default();
    let stripe_client = Client::new(stripe_secret);

    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", user_id)
        .fetch_one(&pool)
        .await
        .unwrap();

    let customer_id = match user.stripe_customer_id {
        Some(id) => id,
        None => return (StatusCode::BAD_REQUEST, "Sem subscrição ativa").into_response(),
    };

    let portal_params = CreateBillingPortalSession::new(stripe::CustomerId::from_explicit_id(customer_id));
    let session = stripe::BillingPortalSession::create(&stripe_client, portal_params).await.unwrap();

    Json(serde_json::json!({ "portal_url": session.url }))
}

pub async fn create_pix_payment(
    State(pool): State<PgPool>,
    ClaimsExtractor(claims): ClaimsExtractor,
    Json(payload): Json<PixRequest>,
) -> impl IntoResponse {
    let user_id: i32 = claims.sub.parse().unwrap();
    let mp_access_token = std::env::var("MERCADO_PAGO_TOKEN").unwrap_or_default();
    
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", user_id)
        .fetch_one(&pool)
        .await
        .unwrap();

    let amount = match payload.plan_type {
        PlanType::Pro => 49.0,
        PlanType::Business => 199.0,
        _ => 0.0,
    };

    if amount == 0.0 {
        return (StatusCode::BAD_REQUEST, "Plano inválido para Pix").into_response();
    }

    let client = reqwest::Client::new();
    let res = client
        .post("https://api.mercadopago.com/v1/payments")
        .bearer_auth(mp_access_token)
        .json(&serde_json::json!({
            "transaction_amount": amount,
            "description": format!("PonteVPN - Plano {:?}", payload.plan_type),
            "payment_method_id": "pix",
            "payer": {
                "email": user.email,
            },
            "external_reference": format!("user_{}", user_id),
            "notification_url": format!("{}/payments/webhook/mp", std::env::var("API_URL").unwrap_or_default()),
        }))
        .send()
        .await
        .unwrap()
        .json::<serde_json::Value>()
        .await
        .unwrap();

    let qr_code = res["point_of_interaction"]["transaction_data"]["qr_code"].as_str().unwrap_or_default();
    let qr_code_base64 = res["point_of_interaction"]["transaction_data"]["qr_code_base64"].as_str().unwrap_or_default();
    let payment_id = res["id"].as_i64().unwrap_or_default();

    Json(serde_json::json!({
        "payment_id": payment_id,
        "qr_code": qr_code,
        "qr_code_base64": qr_code_base64,
        "status": res["status"].as_str().unwrap_or("pending")
    })).into_response()
}
