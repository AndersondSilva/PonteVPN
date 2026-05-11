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
