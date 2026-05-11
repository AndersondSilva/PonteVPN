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

#[derive(Deserialize)]
pub struct VerifyRequest {
    pub token: String,
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

pub async fn verify_email(
    State(pool): State<PgPool>,
    Json(payload): Json<VerifyRequest>,
) -> impl IntoResponse {
    let result = sqlx::query!(
        "UPDATE users SET is_verified = true, verify_token = NULL WHERE verify_token = $1 RETURNING id",
        payload.token
    )
    .fetch_optional(&pool)
    .await
    .unwrap();

    match result {
        Some(_) => (StatusCode::OK, Json(serde_json::json!({"message": "Email verificado com sucesso"}))).into_response(),
        None => (StatusCode::BAD_REQUEST, Json(serde_json::json!({"detail": "Token inválido ou expirado"}))).into_response(),
    }
}

pub async fn me(
    State(pool): State<PgPool>,
    crate::middleware::auth::ClaimsExtractor(claims): crate::middleware::auth::ClaimsExtractor,
) -> impl IntoResponse {
    let user_id: i32 = claims.sub.parse().unwrap();
    
    let user = sqlx::query!(
        "SELECT u.id, u.email, u.is_admin, u.is_free_user, s.plan 
         FROM users u 
         LEFT JOIN subscriptions s ON u.id = s.user_id 
         WHERE u.id = $1", 
        user_id
    )
    .fetch_one(&pool)
    .await
    .unwrap();

    Json(serde_json::json!({
        "id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_free_user": user.is_free_user,
        "plan": user.plan.unwrap_or(crate::models::PlanType::Free),
    }))
}
