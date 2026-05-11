use axum::{
    routing::get,
    Router,
};
use std::net::SocketAddr;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use dotenvy::dotenv;
use sqlx::postgres::PgPoolOptions;
use tower_http::cors::{Any, CorsLayer};

mod models;
mod handlers;
mod services;
mod middleware;
mod utils;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenv().ok();

    // Configurar logs
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Conectar ao banco de dados
    let database_url = std::env::var("DATABASE_URL")
        .expect("DATABASE_URL deve estar definida no .env");
    
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await?;

    // Configurar CORS restrito
    let cors = CorsLayer::new()
        .allow_origin([
            "https://pontevpn.com".parse().unwrap(),
            "https://www.pontevpn.com".parse().unwrap(),
        ])
        .allow_methods([axum::http::Method::GET, axum::http::Method::POST, axum::http::Method::DELETE])
        .allow_headers([axum::http::header::AUTHORIZATION, axum::http::header::CONTENT_TYPE]);

    // Cabeçalhos de Segurança
    let security_headers = tower_http::set_header::SetResponseHeaderLayer::overriding(
        axum::http::header::STRICT_TRANSPORT_SECURITY,
        axum::http::HeaderValue::from_static("max-age=63072000; includeSubDomains; preload"),
    );

    // Rotas
    let app = Router::new()
        .route("/health", get(|| async { "OK" }))
        .nest("/auth", Router::new()
            .route("/register", axum::routing::post(handlers::auth::register))
            .route("/login", axum::routing::post(handlers::auth::login))
            .route("/verify", axum::routing::post(handlers::auth::verify_email))
            .route("/me", axum::routing::get(handlers::auth::me))
            .route("/google", axum::routing::get(handlers::auth_social::google_login))
            .route("/google/callback", axum::routing::get(handlers::auth_social::google_callback))
            .route("/apple", axum::routing::get(handlers::auth_social::apple_login))
        )
        .nest("/servers", Router::new()
            .route("/", axum::routing::get(handlers::servers::list_servers))
        )
        .nest("/vpn", Router::new()
            .route("/configs", axum::routing::get(handlers::vpn::list_configs))
            .route("/generate", axum::routing::post(handlers::vpn::generate_config))
        )
        .nest("/payments", Router::new()
            .route("/checkout", axum::routing::post(handlers::payments::create_checkout))
            .route("/portal", axum::routing::get(handlers::payments::billing_portal))
            .route("/pix", axum::routing::post(handlers::payments::create_pix_payment))
            .route("/webhook/stripe", axum::routing::post(handlers::webhooks::stripe_webhook))
            .route("/webhook/mp", axum::routing::post(handlers::webhooks::mercadopago_webhook))
        )
        .nest("/admin", Router::new()
            .route("/users", axum::routing::get(handlers::admin::list_users))
            .route("/access", axum::routing::post(handlers::admin::set_user_access))
            .route("/toggle-free", axum::routing::post(handlers::admin::toggle_user_free_access))
            .route("/register-server", axum::routing::post(handlers::admin::register_server))
        )
        .layer(cors)
        .layer(security_headers)
        .with_state(pool);

    // Iniciar servidor
    let port = std::env::var("PORT")
        .unwrap_or_else(|_| "8000".to_string())
        .parse()
        .expect("PORT deve ser um número");
    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    tracing::info!("Servidor rodando em {}", addr);
    
    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
