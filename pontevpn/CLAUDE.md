# PonteVPN — Contexto do Projeto para Claude Code

## ⚠️ PASSO OBRIGATÓRIO ANTES DE QUALQUER TRABALHO

Antes de iniciar qualquer tarefa neste projeto, ler e seguir os
princípios definidos em:

```
/Users/anderson/Documents/Projetos/VPN/Claude Code Instruções/
```

Ficheiros a consultar por ordem:
1. `CONSOLIDACAO-FINAL.md` — visão geral do sistema e regras
2. `BACKUP-STRATEGY.md`    — como versionar e fazer backup
3. `BACKUP-QUICK-GUIDE.md` — checklist diário

Princípios que se aplicam a este projeto:
- Segurança SEMPRE em primeiro lugar (validar antes de qualquer ação)
- Versionar tudo: cada mudança relevante tem commit git
- Aprender com falhas: cada problema gera documentação em docs/
- Medir antes de otimizar
- MVP antes de perfeição — seguir a ordem das fases

## O que é este projeto
VPN-as-a-Service focado em brasileiros no exterior que querem acessar
conteúdo geo-bloqueado do Brasil (Globoplay, bancos, serviços públicos)
e o caminho inverso (IPs estrangeiros para quem está no Brasil).

## Stack (não alterar sem motivo claro)
- Backend: FastAPI (Python 3.12) em /backend
- Frontend: Next.js 14 App Router em /frontend
- Database: PostgreSQL via Supabase
- Pagamentos: Stripe (EUR)
- VPN: WireGuard
- Servidores VPN: Hetzner (EU) + Vultr (BR)
- Deploy frontend: Vercel
- Deploy backend: Railway

## Nome do produto
PonteVPN — tagline: "Sua ponte para o conteúdo que você ama"

## Preços (EUR)
- Free: €0 — 1 servidor BR, 2GB/mês
- Pro: €7.99/mês ou €63.99/ano — todos os servidores, ilimitado
- Business: €19.99/mês — 5 dispositivos, todos os servidores

## Regras de segurança (INEGOCIÁVEIS)
1. Chaves privadas WireGuard NUNCA são armazenadas no banco
2. Nenhum log de tráfego, DNS ou IP de destino
3. Secrets sempre em variáveis de ambiente, nunca no código
4. Todos os endpoints autenticados usam JWT Bearer token
5. Rate limiting em todos os endpoints públicos

## Estrutura de pastas
```
pontevpn/
├── backend/          FastAPI + PostgreSQL
├── frontend/         Next.js 14
├── infrastructure/   Scripts de setup de servidores VPN
└── docs/             Legal, Privacy Policy, ToS, Deploy Guide
```

## Conformidade legal (Portugal/EU)
- GDPR obrigatório
- Privacy Policy e ToS em PT-BR e EN
- IVA (VAT) aplicável via Stripe Tax
- Dados de usuários EU armazenados em servidores EU (Hetzner)

## Quando adicionar features
Seguir a ordem das fases no PROMPT-VPN-SAAS.md.
Fase 1 deve estar completa e testada antes de iniciar Fase 2.
