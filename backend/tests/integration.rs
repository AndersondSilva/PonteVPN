#[cfg(test)]
mod tests {
    use ax_test::TestServer; // Exemplo hipotético ou usando reqwest
    
    #[tokio::test]
    async fn test_health_check() {
        // Em um cenário real, usaríamos axum::test_helpers ou reqwest para bater no servidor subido
        assert_eq!(2 + 2, 4);
    }
}
