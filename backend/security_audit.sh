#!/bin/bash
# Script de Auditoria de Segurança PonteVPN

echo "=== Iniciando Auditoria de Segurança ==="

# 1. Auditoria de dependências (cargo-audit)
if command -v cargo-audit &> /dev/null
then
    echo "[1/3] Verificando dependências vulneráveis..."
    cargo audit
else
    echo "[!] cargo-audit não instalado. Instale com: cargo install cargo-audit"
fi

# 2. Linting e boas práticas (clippy)
echo "[2/3] Executando Clippy para análise estática..."
cargo clippy -- -D warnings

# 3. Testes unitários e de integração
echo "[3/3] Executando testes automatizados..."
cargo test

echo "=== Auditoria Concluída ==="
