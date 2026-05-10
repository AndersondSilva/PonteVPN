use axum::{
    extract::{State, Query},
    Json,
    http::StatusCode,
    response::IntoResponse,
};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use chrono::{Utc, Duration};
use crate::models::{User, PlanType, SubStatus};
use crate::utils::auth::{hash_password, verify_password, create_jwt};
use rand::{thread_rng, Rng};
use rand::distributions::Alphanumeric;

#[derive(Deserialize)]
pub struct RegisterRequest {
    pub email: String,
    pub password: String,
}

#[derive(Deserialize)]
pub struct LoginRequest {
    pub email: String,
    pub password: String,
}

#[derive(Serialize)]
pub struct TokenResponse {
    pub access_token: String,
    pub token_type: String,
}

pub async fn register(
    State(pool): State<PgPool>,
    Json(payload): Json<RegisterRequest>,
) -> impl IntoResponse {
    // Verificar se usuário já existe
    let exists = sqlx::query!("SELECT id FROM users WHERE email = $1", payload.email)
        .fetch_optional(&pool)
        .await
        .unwrap();

    if exists.is_some() {
        return (StatusCode::BAD_REQUEST, Json(serde_json::json!({"detail": "Email já registrado"}))).into_response();
    }

    if payload.password.len() < 8 {
        return (StatusCode::BAD_REQUEST, Json(serde_json::json!({"detail": "Senha curta"}))).into_response();
    }

    let hashed = hash_password(&payload.password);
    let verify_token: String = thread_rng()
        .sample_iter(&Alphanumeric)
        .take(32)
        .map(char::from)
        .collect();

    // 30 dias de trial gratuito
    let trial_end = Utc::now() + Duration::days(30);

    // Inserir usuário
    let user_id = sqlx::query!(
        "INSERT INTO users (email, password_hash, verify_token, trial_ends_at, preferred_currency) VALUES ($1, $2, $3, $4, $5) RETURNING id",
        payload.email, hashed, verify_token, trial_end, "BRL".to_string() // Default BRL, alterável depois
    )
    .fetch_one(&pool)
    .await
    .unwrap()
    .id;

    // Criar subscrição free
    sqlx::query!(
        "INSERT INTO subscriptions (user_id, plan, status) VALUES ($1, $2, $3)",
        user_id, PlanType::Free as PlanType, SubStatus::Active as SubStatus
    )
    .execute(&pool)
    .await
    .unwrap();

    (StatusCode::CREATED, Json(serde_json::json!({"message": "Conta criada. Verifique seu email."}))).into_response()
}

pub async fn login(
    State(pool): State<PgPool>,
    Json(payload): Json<LoginRequest>,
) -> impl IntoResponse {
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE email = $1", payload.email)
        .fetch_optional(&pool)
        .await
        .unwrap();

    match user {
        Some(u) if verify_password(&payload.password, &u.password_hash) => {
            if !u.is_verified {
                return (StatusCode::FORBIDDEN, Json(serde_json::json!({"detail": "Email não verificado"}))).into_response();
            }
            
            let secret = std::env::var("SECRET_KEY").unwrap_or_else(|_| "secret".into());
            let token = create_jwt(u.id, &secret).unwrap();
            
            Json(TokenResponse {
                access_token: token,
                token_type: "bearer".into(),
            }).into_response()
        }
        _ => (StatusCode::UNAUTHORIZED, Json(serde_json::json!({"detail": "Credenciais inválidas"}))).into_response(),
    }
}
