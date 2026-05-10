use base64::{engine::general_purpose, Engine as _};
use rand::rngs::OsRng;
use x25519_dalek::{StaticSecret, PublicKey};
use std::net::Ipv4Addr;

pub struct WireGuardService;

impl WireGuardService {
    pub fn generate_keypair() -> (String, String) {
        let private_key = StaticSecret::random_from_rng(OsRng);
        let public_key = PublicKey::from(&private_key);

        let priv_base64 = general_purpose::STANDARD.encode(private_key.to_bytes());
        let pub_base64 = general_purpose::STANDARD.encode(public_key.as_bytes());

        (priv_base64, pub_base64)
    }

    pub fn build_client_config(
        private_key: &str,
        client_vpn_ip: &str,
        server_public_key: &str,
        server_endpoint: &str,
        server_port: i32,
    ) -> String {
        format!(
            r#"[Interface]
PrivateKey = {private_key}
Address = {client_vpn_ip}/32
DNS = 1.1.1.1, 1.0.0.1

[Peer]
PublicKey = {server_public_key}
Endpoint = {server_endpoint}:{server_port}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"#
        )
    }

    pub fn ip_from_index(index: i32) -> String {
        // Base 10.8.1.1 (índice 1 -> 10.8.1.1)
        let base_addr = u32::from(Ipv4Addr::new(10, 8, 1, 0));
        let client_addr = Ipv4Addr::from(base_addr + index as u32);
        client_addr.to_string()
    }

    pub async fn register_peer_on_server(
        agent_url: &str,
        public_key: &str,
        vpn_ip: &str,
        secret: &str,
    ) -> Result<bool, reqwest::Error> {
        let client = reqwest::Client::new();
        let res = client
            .post(format!("{}/peers", agent_url))
            .header("X-Secret", secret)
            .json(&serde_json::json!({
                "public_key": public_key,
                "allowed_ip": format!("{}/32", vpn_ip)
            }))
            .send()
            .await?;

        Ok(res.status().is_success())
    }

    pub async fn remove_peer_from_server(
        agent_url: &str,
        public_key: &str,
        secret: &str,
    ) -> Result<bool, reqwest::Error> {
        let client = reqwest::Client::new();
        let res = client
            .delete(format!("{}/peers/{}", agent_url, public_key))
            .header("X-Secret", secret)
            .send()
            .await?;

        Ok(res.status().is_success())
    }
}
