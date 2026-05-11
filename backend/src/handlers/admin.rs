use axum::{
    extract::{State, Json},
    http::StatusCode,
    response::IntoResponse,
};
use serde::Deserialize;
use sqlx::PgPool;
use chrono::{DateTime, Utc};
use crate::middleware::auth::ClaimsExtractor;

#[derive(Deserialize)]
pub struct SetAccessRequest {
    pub user_id: i32,
    pub expires_at: Option<DateTime<Utc>>,
    pub is_whitelisted: bool,
}

#[derive(Deserialize)]
pub struct ToggleFreeRequest {
    pub user_id: i32,
    pub is_free: bool,
}

#[derive(Deserialize)]
pub struct RegisterServerRequest {
    pub ip: String,
    pub pub_key: String,
    pub agent_url: String,
}

pub async fn set_user_access(
    State(pool): State<PgPool>,
    ClaimsExtractor(claims): ClaimsExtractor,
    Json(payload): Json<SetAccessRequest>,
) -> impl IntoResponse {
    let requester_id: i32 = claims.sub.parse().unwrap();
    
    // Verificar se o solicitante é um admin no banco
    let is_admin = sqlx::query_scalar!("SELECT is_admin FROM users WHERE id = $1", requester_id)
        .fetch_one(&pool)
        .await
        .unwrap_or(false);

    if !is_admin {
        return (StatusCode::FORBIDDEN, "Não autorizado").into_response();
    }

    sqlx::query!(
        "UPDATE users SET trial_ends_at = $1, is_whitelisted = $2 WHERE id = $3",
        payload.expires_at, payload.is_whitelisted, payload.user_id
    )
    .execute(&pool)
    .await
    .unwrap();

    (StatusCode::OK, "Acesso atualizado com sucesso").into_response()
}

pub async fn register_server(
    State(pool): State<PgPool>,
    Header(admin_secret): Header<String>, // Simplificado para este endpoint automático
    Json(payload): Json<RegisterServerRequest>,
) -> impl IntoResponse {
    let secret = std::env::var("VPN_SERVERS_API_SECRET").unwrap_or_default();
    if admin_secret != secret {
        return (StatusCode::FORBIDDEN, "Forbidden").into_response();
    }

    sqlx::query!(
        "INSERT INTO servers (name, country, country_code, city, ip, wg_public_key, agent_url) 
         VALUES ($1, $2, $3, $4, $5, $6, $7)
         ON CONFLICT (ip) DO UPDATE SET wg_public_key = $6, agent_url = $7, is_active = true",
        format!("Auto Node - {}", payload.ip), "Desconhecido", "??", "Desconhecido", 
        payload.ip, payload.pub_key, payload.agent_url
    )
    .execute(&pool)
    .await
    .unwrap();

    (StatusCode::OK, "Server registered").into_response()
}

pub async fn toggle_user_free_access(
    State(pool): State<PgPool>,
    ClaimsExtractor(claims): ClaimsExtractor,
    Json(payload): Json<ToggleFreeRequest>,
) -> impl IntoResponse {
    let requester_id: i32 = claims.sub.parse().unwrap();
    
    let is_admin = sqlx::query_scalar!("SELECT is_admin FROM users WHERE id = $1", requester_id)
        .fetch_one(&pool)
        .await
        .unwrap_or(false);

    if !is_admin {
        return (StatusCode::FORBIDDEN, "Não autorizado").into_response();
    }

    sqlx::query!(
        "UPDATE users SET is_free_user = $1 WHERE id = $2",
        payload.is_free, payload.user_id
    )
    .execute(&pool)
    .await
    .unwrap();

    let status = if payload.is_free { "habilitada" } else { "desabilitada" };
    (StatusCode::OK, format!("Gratuidade {} com sucesso", status)).into_response()
}

pub async fn list_users(
    State(pool): State<PgPool>,
    ClaimsExtractor(claims): ClaimsExtractor,
) -> impl IntoResponse {
    let requester_id: i32 = claims.sub.parse().unwrap();
    
    let is_admin = sqlx::query_scalar!("SELECT is_admin FROM users WHERE id = $1", requester_id)
        .fetch_one(&pool)
        .await
        .unwrap_or(false);

    if !is_admin {
        return (StatusCode::FORBIDDEN, "Não autorizado").into_response();
    }

    let users = sqlx::query_as!(
        crate::models::User,
        "SELECT * FROM users ORDER BY created_at DESC"
    )
    .fetch_all(&pool)
    .await
    .unwrap();

    (StatusCode::OK, Json(users)).into_response()
}
