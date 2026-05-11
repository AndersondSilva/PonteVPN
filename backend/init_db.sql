-- Extensão para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum para tipos de plano
CREATE TYPE plan_type AS ENUM ('free', 'pro', 'business');

-- Enum para status de subscrição
CREATE TYPE sub_status AS ENUM ('active', 'past_due', 'canceled', 'trialing');

-- Enum para ciclo de faturamento
CREATE TYPE billing_cycle AS ENUM ('monthly', 'quarterly', 'yearly');

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verify_token VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    trial_ends_at TIMESTAMPTZ,
    is_whitelisted BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_free_user BOOLEAN DEFAULT FALSE,
    preferred_currency VARCHAR(5) DEFAULT 'BRL',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de Servidores VPN
CREATE TABLE IF NOT EXISTS servers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    country_code VARCHAR(5) NOT NULL,
    city VARCHAR(100) NOT NULL,
    ip VARCHAR(50) UNIQUE NOT NULL,
    wg_port INTEGER DEFAULT 51820,
    wg_public_key VARCHAR(255) NOT NULL,
    agent_url VARCHAR(255) NOT NULL,
    agent_secret VARCHAR(255),
    capacity INTEGER DEFAULT 500,
    active_peers INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    min_plan plan_type DEFAULT 'free'
);

-- Tabela de Subscrições
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan plan_type DEFAULT 'free',
    cycle billing_cycle DEFAULT 'monthly',
    status sub_status DEFAULT 'active',
    stripe_subscription_id VARCHAR(255),
    stripe_price_id VARCHAR(255),
    current_period_end TIMESTAMPTZ,
    bandwidth_used_bytes BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de Configurações VPN (Peers)
CREATE TABLE IF NOT EXISTS vpn_configs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    wg_public_key VARCHAR(255) NOT NULL,
    vpn_ip VARCHAR(50) NOT NULL,
    device_name VARCHAR(100) DEFAULT 'Meu Dispositivo',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inserir servidor inicial de teste (Brasil)
INSERT INTO servers (name, country, country_code, city, ip, wg_public_key, agent_url, min_plan)
VALUES ('São Paulo Core', 'Brasil', 'BR', 'São Paulo', '1.2.3.4', 'public_key_exemplo', 'http://agent.br.pontevpn.com', 'free')
ON CONFLICT DO NOTHING;
