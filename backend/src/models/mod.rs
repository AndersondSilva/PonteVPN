use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize, sqlx::Type, PartialEq)]
#[sqlx(type_name = "plan_type", rename_all = "lowercase")]
pub enum PlanType {
    Free,
    Pro,
    Business,
}

#[derive(Debug, Serialize, Deserialize, sqlx::Type, PartialEq)]
#[sqlx(type_name = "sub_status", rename_all = "snake_case")]
pub enum SubStatus {
    Active,
    PastDue,
    Canceled,
    Trialing,
}

#[derive(Debug, FromRow, Serialize, Deserialize)]
pub struct User {
    pub id: i32,
    pub email: String,
    pub password_hash: String,
    pub is_verified: bool,
    pub verify_token: Option<String>,
    pub stripe_customer_id: Option<String>,
    pub trial_ends_at: Option<DateTime<Utc>>,
    pub is_whitelisted: bool,
    pub is_admin: bool,
    pub is_free_user: bool,
    pub preferred_currency: String, // "BRL" ou "EUR"
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::Type, PartialEq)]
#[sqlx(type_name = "billing_cycle", rename_all = "lowercase")]
pub enum BillingCycle {
    Monthly,
    Quarterly,
    Yearly,
}

#[derive(Debug, FromRow, Serialize, Deserialize)]
pub struct Subscription {
    pub id: i32,
    pub user_id: i32,
    pub plan: PlanType,
    pub cycle: BillingCycle,
    pub status: SubStatus,
    pub stripe_subscription_id: Option<String>,
    pub stripe_price_id: Option<String>,
    pub current_period_end: Option<DateTime<Utc>>,
    pub bandwidth_used_bytes: i64,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, FromRow, Serialize, Deserialize)]
pub struct Server {
    pub id: i32,
    pub name: String,
    pub country: String,
    pub country_code: String,
    pub city: String,
    pub ip: String,
    pub wg_port: i32,
    pub wg_public_key: String,
    pub agent_url: String,
    pub agent_secret: Option<String>,
    pub capacity: i32,
    pub active_peers: i32,
    pub is_active: bool,
    pub min_plan: PlanType,
}

#[derive(Debug, FromRow, Serialize, Deserialize)]
pub struct VPNConfig {
    pub id: i32,
    pub user_id: i32,
    pub server_id: i32,
    pub wg_public_key: String,
    pub vpn_ip: String,
    pub device_name: String,
    pub is_active: bool,
    pub created_at: DateTime<Utc>,
}
