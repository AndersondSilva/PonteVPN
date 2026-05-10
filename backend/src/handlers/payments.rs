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
    checkout_params.payment_method_types = Some(vec![stripe::CheckoutSessionPaymentMethodType::Card]);
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

    let app_url = std::env::var("APP_URL").unwrap_or_default();
    let portal_params = CreateBillingPortalSession::new(stripe::CustomerId::from_explicit_id(customer_id));
    let session = stripe::BillingPortalSession::create(&stripe_client, portal_params).await.unwrap();

    Json(serde_json::json!({ "portal_url": session.url }))
}

// Mercado Pago Pix (Esqueleto)
pub async fn create_pix_payment() -> impl IntoResponse {
    // Integração com a API do Mercado Pago para gerar QR Code Pix
    Json(serde_json::json!({ "qr_code": "placeholder", "qr_code_base64": "placeholder" }))
}
