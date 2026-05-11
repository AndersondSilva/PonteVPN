# VPN-as-a-Service — Instruções para Claude Code
# v2.0 | Security-First | Phased Execution

---

## ⚠️ PASSO 0 — OBRIGATÓRIO ANTES DE QUALQUER TAREFA

Ler e aplicar os princípios da pasta:

```
/Users/anderson/Documents/Projetos/VPN/Claude Code Instruções/
```

Ordem de leitura:
1. `CONSOLIDACAO-FINAL.md`  — sistema completo e regras mestras
2. `BACKUP-STRATEGY.md`     — versionamento e backup
3. `BACKUP-QUICK-GUIDE.md`  — uso diário

Princípios que regem este projeto (extraídos das instruções):
- Segurança valida PRIMEIRO — se falhar, parar tudo
- Cada mudança tem commit git antes de continuar
- Falhas geram documentação (post-mortem em docs/)
- Usar o modelo adequado à complexidade da tarefa
- Seguir a ordem das fases — nunca saltar para Fase 2 sem Fase 1 validada

---

## MISSÃO DO PROJETO

Construir uma plataforma completa de VPN como serviço (VPNaaS),
com infraestrutura escalável, site de vendas, pagamentos e
operação automatizada — do MVP até escala de produção.

Este documento é o briefing técnico e de negócio do projeto.
Siga-o como fonte de verdade para todas as decisões.

---

## REGRA #1: SEGURANÇA SEMPRE PRIMEIRO

Antes de qualquer implementação, validar:

[ ] Dados de usuário estão criptografados (AES-256)?
[ ] Chaves privadas nunca aparecem em logs?
[ ] LGPD (Brasil) e GDPR (Europa) estão sendo respeitadas?
[ ] Firewall isola cada servidor VPN dos demais?
[ ] Rate limiting protege todos os endpoints públicos?
[ ] Segredos estão em Vault/Secrets Manager, não em .env?

Se qualquer item falhar → parar e resolver antes de continuar.

---

## CONTEXTO DE NEGÓCIO

### Mercado-Alvo

**Primário:** Brasileiros vivendo no exterior que querem acessar
conteúdo geo-bloqueado para o Brasil — streaming (Globoplay, SBT+,
Paramount+ BR), bancos brasileiros, serviços públicos e e-commerce.

**Secundário:** Estrangeiros ou viajantes que estão fora do Brasil
e querem um IP brasileiro para acessar conteúdo ou serviços
disponíveis apenas na região.

**Terciário:** Qualquer pessoa que precise de um IP de outro país
para acessar conteúdo geo-restrito (o caminho inverso também é
suportado — IP brasileiro para fora, IP estrangeiro para dentro).

### Posicionamento Competitivo
A plataforma deve vencer em 3 dimensões:
1. VELOCIDADE: latência < 20ms para servidores BR
2. SIMPLICIDADE: cliente conectado em < 60 segundos
3. TRANSPARÊNCIA: status de servidores público e em tempo real

### Modelo de Negócio

```
PLANO FREE     | R$ 0/mês   | 1 país, 1GB/mês, sem suporte
PLANO BÁSICO   | R$ 19/mês  | 5 países, 50GB, suporte email
PLANO PRO      | R$ 49/mês  | Todos os países, ilimitado, suporte prioritário
PLANO BUSINESS | R$ 199/mês | Multi-seat, API access, SLA 99.9%
```

### KPIs de Sucesso (Medir Mensalmente)

```
MÊS 1:  10 usuários pagantes | MRR R$ 500   | Uptime 99%
MÊS 3:  100 usuários         | MRR R$ 4.000 | Latência < 30ms
MÊS 6:  500 usuários         | MRR R$ 20k   | Churn < 5%
MÊS 12: 2.000 usuários       | MRR R$ 80k   | NPS > 50
```

---

## STACK TECNOLÓGICO (DEFINITIVO — SEM ALTERNATIVAS)

```
Backend API:      FastAPI (Python 3.12) + Pydantic v2
Frontend:         Next.js 14 (App Router) + Tailwind CSS + shadcn/ui
Database:         PostgreSQL 16 (primário) + Redis 7 (cache/sessões)
VPN Layer:        WireGuard (protocolo principal) + SoftEther (fallback)
Infraestrutura:   Terraform + Ansible + Docker + GitHub Actions (CI/CD)
Monitoramento:    Prometheus + Grafana + Loki (logs)
Pagamentos:       Stripe (internacional) + Mercado Pago (Brasil)
Secrets:          HashiCorp Vault (produção) | .env criptografado (dev)
Cloud Provider:   Hetzner (servidores VPN EU) + Vultr (BR + outros)
DNS:              Cloudflare (proteção DDoS incluída)
```

**Justificativas:**
- FastAPI: performance superior ao Express para I/O assíncrono
- WireGuard: kernel-space, 3x mais rápido que OpenVPN
- Hetzner: melhor custo/GB na Europa (essencial para margem)
- Cloudflare: DDoS mitigation gratuito no plano Pro

---

## IMPLEMENTAÇÃO EM 3 FASES

### FASE 1 — MVP (Semanas 1-4)
**Meta:** Primeiro cliente pagante

```
Semana 1: Infraestrutura Base
├── [ ] Terraform: 1 servidor VPN no Brasil (Vultr São Paulo)
├── [ ] Terraform: 1 servidor VPN na Europa (Hetzner Falkenstein)
├── [ ] WireGuard instalado e configurado em ambos
├── [ ] Firewall: apenas portas 51820/UDP e 22/TCP (jump server)
└── [ ] Teste manual de conectividade BR↔EU

Semana 2: Backend Core
├── [ ] FastAPI + PostgreSQL (Docker Compose local)
├── [ ] Modelo de dados: User, Subscription, Server, VPNConfig
├── [ ] Auth: JWT + refresh tokens (sem OAuth ainda)
├── [ ] API: POST /users, POST /auth/login, GET /servers
└── [ ] API: POST /vpn/generate-config (cria par de chaves WireGuard)

Semana 3: Frontend + Pagamentos
├── [ ] Landing page (Next.js) com pricing table
├── [ ] Dashboard do usuário: download de config, status
├── [ ] Stripe Checkout integrado (planos Basic e Pro)
├── [ ] Webhook Stripe: ativa/desativa VPN config por status
└── [ ] Email transacional: boas-vindas, renovação, cancelamento

Semana 4: Estabilização
├── [ ] Deploy produção: Railway (backend) + Vercel (frontend)
├── [ ] Monitoramento básico: Uptime Robot + Sentry
├── [ ] Documentação: como instalar config no iPhone/Android/Windows
├── [ ] Beta test: 5 usuários reais (amigos/família)
└── [ ] Correção de bugs críticos antes de lançar
```

**Critério de saída da Fase 1:**
- 1 usuário pagante com VPN funcionando
- Uptime 95%+ por 7 dias consecutivos

---

### FASE 2 — ESCALA (Meses 2-4)
**Meta:** 100 usuários pagantes, operação automatizada

```
Infraestrutura:
├── [ ] Auto-provisioning: novo servidor em < 5 minutos (Ansible)
├── [ ] 3+ localizações: Brasil, Alemanha, EUA, Holanda
├── [ ] Load balancer: distribuir usuários por servidor
├── [ ] Alertas: PagerDuty se servidor cair
└── [ ] Backup automático de configs e banco

Produto:
├── [ ] Arquivo .conf para WireGuard (iOS/Android/Desktop)
├── [ ] Seleção de servidor por localização no dashboard
├── [ ] Uso de bandwidth em tempo real no dashboard
├── [ ] Plano Free com hard limit de 1GB (corta automaticamente)
└── [ ] Upgrade/downgrade de plano sem perder config

Negócio:
├── [ ] Mercado Pago integrado (Pix + boleto para BR)
├── [ ] Afiliados: 30% de comissão recorrente
├── [ ] Admin panel: gerenciar usuários, ver métricas, banir abusos
└── [ ] Política de privacidade revisada por advogado (LGPD)
```

---

### FASE 3 — ENTERPRISE (Meses 5-12)
**Meta:** R$ 80k MRR, produto competitivo internacionalmente

```
Infraestrutura:
├── [ ] Kubernetes para orquestração de servidores VPN
├── [ ] 10+ países: Ásia, América Latina, Oceania
├── [ ] BGP anycast para routing inteligente
└── [ ] SLA 99.9% com crédito automático em caso de falha

Produto:
├── [ ] App nativo iOS + Android (React Native)
├── [ ] Kill switch automático
├── [ ] Split tunneling (rotear só apps específicos pelo VPN)
├── [ ] API pública para clientes Business (BYOD VPN)
└── [ ] Multi-sede: até 50 conexões simultâneas por conta Business

Segurança:
├── [ ] Auditoria de segurança externa (Penetration Test)
├── [ ] Warrant canary público atualizado mensalmente
├── [ ] Zero-knowledge architecture validada
└── [ ] ISO 27001 roadmap iniciado
```

---

## ARQUITETURA DE SEGURANÇA (IMUTÁVEL)

### Zero-Knowledge VPN Design

```
Usuário → [WireGuard Tunnel] → Servidor VPN → Internet
            ↑                      ↑
    Chave gerada no              Sem logs de
    dispositivo do              conexão ou IP
    usuário. A chave            de destino.
    privada nunca               Apenas timestamp
    sai do dispositivo.         de conexão ativa.
```

### O que REGISTRAR (Necessário para operar):
- Email do usuário + hash de senha (bcrypt rounds=12)
- Data de início e fim de assinatura
- Bytes transferidos (para limitar plano Free)
- Chave pública WireGuard (não a privada)
- Servidor selecionado pelo usuário

### O que NUNCA REGISTRAR:
- IPs de destino visitados
- DNS queries
- Horários de conexão por sessão
- Chaves privadas de qualquer tipo

### Conformidade Legal:
- LGPD (Brasil): DPA nomeado, privacy policy em PT-BR, direito de exclusão
- GDPR (Europa): cookie consent, data processing agreement com servidores EU
- Retenção de dados: 90 dias máximo para dados de billing, 0 para tráfego

---

## AUTOMAÇÕES OBRIGATÓRIAS

### 1. Server Lifecycle

```
ON servidor_load > 80%:
    → Provisionar novo servidor na mesma região (Ansible)
    → Migrar 30% dos usuários automaticamente
    → Alertar via Slack

ON servidor_offline > 2min:
    → Migrar usuários para servidor backup
    → Criar ticket de investigação
    → Notificar usuários afetados por email
```

### 2. User Lifecycle

```
ON pagamento_aprovado:
    → Ativar VPN config do usuário
    → Enviar email de boas-vindas com guia de instalação
    → Criar registro de uso no Prometheus

ON pagamento_falhou:
    → Email D+0, D+3, D+7 com link de pagamento
    → Suspender config no D+7 (não deletar)
    → Reativar imediatamente se pagamento regularizado

ON bandwidth_limit_atingido (plano free):
    → Throttle para 128Kbps (não cortar totalmente)
    → Email com call-to-action para upgrade
    → Banner no dashboard
```

### 3. Abuse Detection

```
ON usuário_enviando > 10GB/hora:
    → Flag como possível abuso
    → Throttle automático para investigação
    → Notificar admin

ON múltiplas_conexões_simultâneas > plano_permite:
    → Derrubar conexão mais antiga
    → Log do evento para análise
```

---

## MONITORAMENTO E OBSERVABILIDADE

### Dashboards Grafana Obrigatórios

```
PAINEL 1: Saúde da Rede
├── Latência por servidor (ms) — alerta se > 50ms
├── Packet loss por servidor (%) — alerta se > 1%
├── Conexões ativas por servidor — alerta se > 80% capacity
└── Uptime por servidor (%) — alerta se < 99%

PAINEL 2: Negócio em Tempo Real
├── MRR atual vs meta do mês
├── Novos usuários hoje / semana / mês
├── Churn rate (últimos 30 dias)
└── Bandwidth total consumido por tier

PAINEL 3: Segurança
├── Failed login attempts (rate por IP)
├── API requests por endpoint (detectar scraping)
├── Usuários com comportamento anômalo
└── Servidores com tráfego suspeito
```

### Níveis de Alerta

```
CRÍTICO (resposta imediata):
- Servidor VPN offline > 2 minutos
- Database connection failed
- Payment processor down

ALTO (resposta em horário comercial):
- Latência > 100ms por 5+ minutos
- Taxa de erro API > 5%
- Usuário sem conseguir conectar após 3 tentativas

MÉDIO (relatório diário):
- Bandwidth acima de 90% da capacidade
- Churn aumentou > 2% semana a semana
- Usuário com comportamento suspeito flagado
```

---

## ESTRATÉGIA DE AQUISIÇÃO DE USUÁRIOS

### Canal 1 — Conteúdo Orgânico (Mês 1-3)
- Blog técnico: "Como configurar WireGuard no Brasil"
- YouTube: tutoriais de privacidade e VPN
- Reddit r/brasil + r/privacy: presença autêntica

### Canal 2 — Afiliados (Mês 2-6)
- 30% de comissão recorrente para criadores de conteúdo tech
- Painel de afiliados com tracking em tempo real

### Canal 3 — Performance Marketing (Mês 4+)
- Google Ads: "vpn brasil", "vpn netflix", "vpn barata"
- Meta Ads: audiences de expats brasileiros

---

## FORMATO DE ENTREGA

Para cada módulo implementado, entregar obrigatoriamente:

```
1. CÓDIGO FUNCIONAL
   └── Testado, com comentários em pontos não-óbvios

2. SCRIPT DE DEPLOY
   └── Um comando para subir em produção

3. TESTE DE VALIDAÇÃO
   └── Como confirmar que funciona corretamente

4. CHECKLIST DE SEGURANÇA
   └── O que foi validado antes de ir para produção

5. MÉTRICAS DE SUCESSO
   └── Como saber se este módulo está funcionando bem
```

---

## PRINCÍPIOS DE EVOLUÇÃO

1. VERSIONAR TUDO: cada mudança em infraestrutura tem tag git
2. ROLLBACK EM 1 COMANDO: qualquer deploy pode ser revertido
3. APRENDER COM FALHAS: cada outage gera um post-mortem documentado
4. MEDIR ANTES DE OTIMIZAR: não otimizar o que não está medido
5. MVP BEFORE PERFECTION: funcional > perfeito na Fase 1

---

## RESTRIÇÕES INEGOCIÁVEIS

Proibido em qualquer circunstância:
- Armazenar chaves privadas de usuários
- Logar tráfego ou destinos de conexão
- Compartilhar dados com terceiros sem consentimento explícito
- Fazer deploy em produção sem smoke test básico
- Implementar feature da Fase 3 antes de validar a Fase 1

---

STATUS INICIAL: FASE 1 | Semana 1 | Infraestrutura Base
PRÓXIMA AÇÃO: Provisionar servidores VPN BR + EU com Terraform
