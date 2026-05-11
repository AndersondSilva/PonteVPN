use axum::{
    extract::{State, Json, Header},
    http::StatusCode,
    response::IntoResponse,
};
use sqlx::PgPool;
use crate::models::{Subscription, PlanType, SubStatus};
use chrono::{Utc, Duration};

pub async fn stripe_webhook(
    State(pool): State<PgPool>,
    body: String,
) -> impl IntoResponse {
    // Em produção, deve-se validar a assinatura do Stripe
    let event: serde_json::Value = serde_json::from_str(&body).unwrap();
    
    let event_type = event["type"].as_str().unwrap();
    let data_object = &event["data"]["object"];

    match event_type {
        "checkout.session.completed" => {
            let customer_id = data_object["customer"].as_str().unwrap();
            let subscription_id = data_object["subscription"].as_str().unwrap();
            
            // Buscar usuário pelo stripe_customer_id
            let user_id = sqlx::query_scalar!("SELECT id FROM users WHERE stripe_customer_id = $1", customer_id)
                .fetch_one(&pool)
                .await
                .unwrap();

            // Atualizar subscrição (simplificado)
            sqlx::query!(
                "UPDATE subscriptions SET status = $1, stripe_subscription_id = $2 WHERE user_id = $3",
                SubStatus::Active as SubStatus, subscription_id, user_id
            )
            .execute(&pool)
            .await
            .unwrap();
        }
        "customer.subscription.deleted" => {
            let subscription_id = data_object["id"].as_str().unwrap();
            
            sqlx::query!(
                "UPDATE subscriptions SET status = $1 WHERE stripe_subscription_id = $2",
                SubStatus::Canceled as SubStatus, subscription_id
            )
            .execute(&pool)
            .await
            .unwrap();
        }
        _ => {}
    }

    StatusCode::OK
}

pub async fn mercadopago_webhook(
    State(pool): State<PgPool>,
    Json(payload): Json<serde_json::Value>,
) -> impl IntoResponse {
    // O Mercado Pago envia um ID de pagamento, precisamos consultar o status real
    if payload["type"] == "payment" {
        let payment_id = payload["data"]["id"].as_str().unwrap_or_default();
        let mp_token = std::env::var("MERCADO_PAGO_TOKEN").unwrap_or_default();
        
        let client = reqwest::Client::new();
        let res = client
            .get(format!("https://api.mercadopago.com/v1/payments/{}", payment_id))
            .bearer_auth(mp_token)
            .send()
            .await
            .unwrap()
            .json::<serde_json::Value>()
            .await
            .unwrap();

        if res["status"] == "approved" {
            let external_ref = res["external_reference"].as_str().unwrap_or_default(); // "user_123"
            if let Some(user_id_str) = external_ref.strip_prefix("user_") {
                let user_id: i32 = user_id_str.parse().unwrap_or(0);
                
                sqlx::query!(
                    "UPDATE subscriptions SET status = $1 WHERE user_id = $2",
                    SubStatus::Active as SubStatus, user_id
                )
                .execute(&pool)
                .await
                .unwrap();
            }
        }
    }

    StatusCode::OK
}
