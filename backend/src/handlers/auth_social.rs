use axum::{
    extract::{State, Query},
    response::Redirect,
};
use serde::Deserialize;
use sqlx::PgPool;
use crate::models::{User, Subscription, PlanType, SubStatus};
use crate::utils::auth::{create_jwt, hash_password};
use rand::{thread_rng, Rng};
use rand::distributions::Alphanumeric;

#[derive(Deserialize)]
pub struct CallbackParams {
    pub code: String,
}

pub async fn google_login() -> Redirect {
    let client_id = std::env::var("GOOGLE_CLIENT_ID").unwrap_or_default();
    let api_url = std::env::var("API_URL").unwrap_or_default();
    let redirect_uri = format!("{}/auth/google/callback", api_url);
    
    let scope = "openid email profile";
    let url = format!(
        "https://accounts.google.com/o/oauth2/v2/auth?client_id={}&redirect_uri={}&response_type=code&scope={}&access_type=offline&prompt=select_account",
        client_id, redirect_uri, scope
    );
    
    Redirect::to(&url)
}

pub async fn google_callback(
    State(pool): State<PgPool>,
    Query(params): Query<CallbackParams>,
) -> Redirect {
    let client_id = std::env::var("GOOGLE_CLIENT_ID").unwrap_or_default();
    let client_secret = std::env::var("GOOGLE_CLIENT_SECRET").unwrap_or_default();
    let api_url = std::env::var("API_URL").unwrap_or_default();
    let app_url = std::env::var("APP_URL").unwrap_or_default();
    let redirect_uri = format!("{}/auth/google/callback", api_url);

    let client = reqwest::Client::new();
    
    // 1. Trocar código por token
    let token_res = client
        .post("https://oauth2.googleapis.com/token")
        .form(&[
            ("code", params.code.as_str()),
            ("client_id", client_id.as_str()),
            ("client_secret", client_secret.as_str()),
            ("redirect_uri", redirect_uri.as_str()),
            ("grant_type", "authorization_code"),
        ])
        .send()
        .await
        .unwrap()
        .json::<serde_json::Value>()
        .await
        .unwrap();

    let access_token = token_res["access_token"].as_str().unwrap();

    // 2. Buscar info do usuário
    let user_info = client
        .get("https://www.googleapis.com/oauth2/v3/userinfo")
        .bearer_auth(access_token)
        .send()
        .await
        .unwrap()
        .json::<serde_json::Value>()
        .await
        .unwrap();

    let email = user_info["email"].as_str().unwrap();

    // 3. Criar ou encontrar usuário
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE email = $1", email)
        .fetch_optional(&pool)
        .await
        .unwrap();

    let user_id = match user {
        Some(u) => {
            if !u.is_verified {
                sqlx::query!("UPDATE users SET is_verified = true WHERE id = $1", u.id)
                    .execute(&pool)
                    .await
                    .unwrap();
            }
            u.id
        }
        None => {
            let random_pass: String = thread_rng().sample_iter(&Alphanumeric).take(32).map(char::from).collect();
            let hashed = hash_password(&random_pass);
            
            let id = sqlx::query!(
                "INSERT INTO users (email, password_hash, is_verified) VALUES ($1, $2, true) RETURNING id",
                email, hashed
            )
            .fetch_one(&pool)
            .await
            .unwrap()
            .id;

            sqlx::query!(
                "INSERT INTO subscriptions (user_id, plan, status) VALUES ($1, $2, $3)",
                id, PlanType::Free as PlanType, SubStatus::Active as SubStatus
            )
            .execute(&pool)
            .await
            .unwrap();
            
            id
        }
    };

    // 4. Gerar JWT e redirecionar
    let secret = std::env::var("SECRET_KEY").unwrap_or_else(|_| "secret".into());
    let token = create_jwt(user_id, &secret).unwrap();
    
    Redirect::to(&format!("{}/auth/callback?token={}", app_url, token))
}

// Apple Login (Esqueleto - Requer configuração de chaves .p8)
pub async fn apple_login() -> Redirect {
    // A implementação do Apple Login é similar, mas requer geração de client_secret assinado com chave privada .p8
    // Redireciona para o endpoint da Apple
    Redirect::to("https://appleid.apple.com/auth/authorize")
}
