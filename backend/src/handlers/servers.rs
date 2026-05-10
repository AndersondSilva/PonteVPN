use axum::{
    extract::State,
    Json,
};
use serde::Serialize;
use sqlx::PgPool;
use crate::models::{Server, Subscription, PlanType};
use crate::middleware::auth::ClaimsExtractor;
use std::collections::HashMap;

#[derive(Serialize)]
pub struct ServerOut {
    pub id: i32,
    pub name: String,
    pub country: String,
    pub country_code: String,
    pub city: String,
    pub flag: String,
    pub is_available: bool,
    pub load_percent: i32,
}

pub async fn list_servers(
    State(pool): State<PgPool>,
    ClaimsExtractor(claims): ClaimsExtractor,
) -> Json<Vec<ServerOut>> {
    let user_id: i32 = claims.sub.parse().unwrap();

    // Buscar plano do usuário
    let sub = sqlx::query_as!(
        Subscription,
        "SELECT * FROM subscriptions WHERE user_id = $1 ORDER BY id DESC LIMIT 1",
        user_id
    )
    .fetch_optional(&pool)
    .await
    .unwrap();

    let user_plan = sub.map(|s| s.plan).unwrap_or(PlanType::Free);

    let servers = sqlx::query_as!(Server, "SELECT * FROM servers WHERE is_active = true")
        .fetch_all(&pool)
        .await
        .unwrap();

    let mut flags = HashMap::new();
    flags.insert("BR", "🇧🇷");
    flags.insert("DE", "🇩🇪");
    flags.insert("NL", "🇳🇱");
    flags.insert("US", "🇺🇸");

    let plan_order = |p: &PlanType| match p {
        PlanType::Free => 0,
        PlanType::Pro => 1,
        PlanType::Business => 2,
    };

    let result = servers
        .into_iter()
        .map(|s| ServerOut {
            id: s.id,
            name: s.name,
            country: s.country,
            country_code: s.country_code.clone(),
            city: s.city,
            flag: flags.get(s.country_code.as_str()).unwrap_or(&"🌐").to_string(),
            is_available: plan_order(&user_plan) >= plan_order(&s.min_plan),
            load_percent: (s.active_peers as f32 / s.capacity as f32 * 100.0) as i32,
        })
        .collect();

    Json(result)
}
