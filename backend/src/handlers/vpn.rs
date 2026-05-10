use axum::{
    extract::State,
    Json,
    http::{StatusCode, header},
    response::{IntoResponse, Response},
};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use crate::models::{User, Server, VPNConfig, Subscription, PlanType, SubStatus};
use chrono::Utc;
use crate::middleware::auth::ClaimsExtractor;
use crate::services::wireguard::WireGuardService;

#[derive(Deserialize)]
pub struct GenerateConfigRequest {
    pub server_id: i32,
    pub device_name: Option<String>,
}

#[derive(Serialize)]
pub struct ConfigOut {
    pub id: i32,
    pub server_name: String,
    pub server_country: String,
    pub country_code: String,
    pub device_name: String,
    pub vpn_ip: String,
    pub is_active: bool,
}

pub async fn list_configs(
    State(pool): State<PgPool>,
    ClaimsExtractor(claims): ClaimsExtractor,
) -> Json<Vec<ConfigOut>> {
    let user_id: i32 = claims.sub.parse().unwrap();

    let rows = sqlx::query!(
        r#"
        SELECT c.id, c.device_name, c.vpn_ip, c.is_active, s.name as server_name, s.country, s.country_code
        FROM vpn_configs c
        JOIN servers s ON c.server_id = s.id
        WHERE c.user_id = $1 AND c.is_active = true
        "#,
        user_id
    )
    .fetch_all(&pool)
    .await
    .unwrap();

    let result = rows
        .into_iter()
        .map(|r| ConfigOut {
            id: r.id,
            server_name: r.server_name,
            server_country: r.country,
            country_code: r.country_code,
            device_name: r.device_name,
            vpn_ip: r.vpn_ip,
            is_active: r.is_active,
        })
        .collect();

    Json(result)
}

pub async fn generate_config(
    State(pool): State<PgPool>,
    ClaimsExtractor(claims): ClaimsExtractor,
    Json(payload): Json<GenerateConfigRequest>,
) -> impl IntoResponse {
    let user_id: i32 = claims.sub.parse().unwrap();

    // 1. Verificar plano e limites
    let sub = sqlx::query_as!(
        Subscription,
        "SELECT * FROM subscriptions WHERE user_id = $1 ORDER BY id DESC LIMIT 1",
        user_id
    )
    .fetch_optional(&pool)
    .await
    .unwrap();

    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", user_id)
        .fetch_one(&pool)
        .await
        .unwrap();

    let user_plan = sub.as_ref().map(|s| &s.plan).unwrap_or(&PlanType::Free);
    let sub_status = sub.as_ref().map(|s| &s.status).unwrap_or(&SubStatus::Active);

    // Permite acesso se: Whitelisted OU Trial ativo OU Subscrição ativa
    let has_access = user.is_whitelisted || 
                     (user.trial_ends_at.is_some() && user.trial_ends_at.unwrap() > Utc::now()) || 
                     (*sub_status == SubStatus::Active || *sub_status == SubStatus::Trialing);

    if !has_access {
        return (StatusCode::FORBIDDEN, "Acesso expirado. Adquira um plano para continuar.").into_response();
    }

    let config_count = sqlx::query!("SELECT count(*) FROM vpn_configs WHERE user_id = $1 AND is_active = true", user_id)
        .fetch_one(&pool)
        .await
        .unwrap()
        .count
        .unwrap();

    let max_configs = match user_plan {
        PlanType::Free => 1,
        PlanType::Pro => 5,
        PlanType::Business => 20,
    };

    if config_count >= max_configs {
        return (StatusCode::FORBIDDEN, format!("Limite de {} atingido", max_configs)).into_response();
    }

    // 2. Buscar servidor
    let server = sqlx::query_as!(Server, "SELECT * FROM servers WHERE id = $1 AND is_active = true", payload.server_id)
        .fetch_optional(&pool)
        .await
        .unwrap();

    let server = match server {
        Some(s) => s,
        None => return (StatusCode::NOT_FOUND, "Servidor não encontrado").into_response(),
    };

    // 3. Gerar chaves e IP
    let (priv_key, pub_key) = WireGuardService::generate_keypair();
    let total_configs = sqlx::query!("SELECT count(*) FROM vpn_configs")
        .fetch_one(&pool)
        .await
        .unwrap()
        .count
        .unwrap();
    let vpn_ip = WireGuardService::ip_from_index(total_configs as i32 + 1);

    // 4. Registrar no servidor
    let secret = std::env::var("VPN_SERVERS_API_SECRET").unwrap_or_default();
    let success = WireGuardService::register_peer_on_server(&server.agent_url, &pub_key, &vpn_ip, &secret).await;

    if let Ok(true) = success {
        let device_name = payload.device_name.unwrap_or_else(|| "Meu Dispositivo".into());
        
        sqlx::query!(
            "INSERT INTO vpn_configs (user_id, server_id, wg_public_key, vpn_ip, device_name) VALUES ($1, $2, $3, $4, $5)",
            user_id, server.id, pub_key, vpn_ip, device_name
        )
        .execute(&pool)
        .await
        .unwrap();

        let conf = WireGuardService::build_client_config(&priv_key, &vpn_ip, &server.wg_public_key, &server.ip, server.wg_port);
        
        let filename = format!("pontevpn-{}.conf", server.country_code.to_lowercase());
        
        Response::builder()
            .header(header::CONTENT_TYPE, "text/plain")
            .header(header::CONTENT_DISPOSITION, format!("attachment; filename=\"{}\"", filename))
            .body(conf.into())
            .unwrap()
            .into_response()
    } else {
        (StatusCode::SERVICE_UNAVAILABLE, "Erro ao registrar peer").into_response()
    }
}
