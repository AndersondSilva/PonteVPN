use axum::{
    async_trait,
    extract::FromRequestParts,
    http::request::Parts,
    http::StatusCode,
};
use jsonwebtoken::{decode, DecodingKey, Validation};
use crate::utils::auth::Claims;

pub struct ClaimsExtractor(pub Claims);

#[async_trait]
impl<S> FromRequestParts<S> for ClaimsExtractor
where
    S: Send + Sync,
{
    type Rejection = (StatusCode, String);

    async fn from_request_parts(parts: &Parts, _state: &S) -> Result<Self, Self::Rejection> {
        let auth_header = parts
            .headers
            .get("Authorization")
            .and_then(|h| h.to_str().ok())
            .ok_or((StatusCode::UNAUTHORIZED, "Token ausente".into()))?;

        if !auth_header.starts_with("Bearer ") {
            return Err((StatusCode::UNAUTHORIZED, "Formato de token inválido".into()));
        }

        let token = &auth_header[7..];
        let secret = std::env::var("SECRET_KEY").unwrap_or_else(|_| "secret".into());

        let token_data = decode::<Claims>(
            token,
            &DecodingKey::from_secret(secret.as_ref()),
            &Validation::default(),
        )
        .map_err(|_| (StatusCode::UNAUTHORIZED, "Token inválido".into()))?;

        Ok(ClaimsExtractor(token_data.claims))
    }
}
