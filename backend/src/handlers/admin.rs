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

pub async fn set_user_access(
    State(pool): State<PgPool>,
    ClaimsExtractor(claims): ClaimsExtractor,
    Json(payload): Json<SetAccessRequest>,
) -> impl IntoResponse {
    // Verificar se o solicitante é um admin (simplificado: checar email ou flag no banco)
    let requester_id: i32 = claims.sub.parse().unwrap();
    let requester = sqlx::query!("SELECT email FROM users WHERE id = $1", requester_id)
        .fetch_one(&pool)
        .await
        .unwrap();

    // Apenas emails específicos podem administrar (mude para o seu email)
    if requester.email != "seu-email-admin@pontevpn.com" {
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
