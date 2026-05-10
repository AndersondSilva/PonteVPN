# Guia de Deploy — PonteVPN
# Do zero ao ar em ~2 horas

---

## CONTAS NECESSÁRIAS (todas gratuitas para começar)

| Serviço | URL | Custo |
|---------|-----|-------|
| Vercel (frontend) | vercel.com | Grátis |
| Railway (backend) | railway.app | $5/mês |
| Supabase (database) | supabase.com | Grátis |
| Stripe (pagamentos) | stripe.com | 1,5% + €0,25 por transação |
| Resend (email) | resend.com | Grátis até 3.000 emails/mês |
| Hetzner (servidor VPN) | hetzner.com | €4,51/mês |
| Cloudflare (DNS) | cloudflare.com | Grátis |
| Domínio | porkbun.com ou namecheap.com | ~€10/ano |

**Custo total Mês 1: ~€15/mês + domínio**

---

## PASSO 1 — Domínio e DNS (15 min)

1. Comprar domínio `pontevpn.com` (ou o nome que preferir) em Porkbun
2. Criar conta no Cloudflare
3. Adicionar o domínio ao Cloudflare
4. No Porkbun, mudar os nameservers para os da Cloudflare
5. No Cloudflare, criar registos DNS:
   ```
   Tipo  Nome    Conteúdo              Proxy
   A     @       [IP do servidor VPS]  ✅
   A     www     [IP do servidor VPS]  ✅
   A     api     [IP do Railway]       ❌ (DNS only)
   ```

---

## PASSO 2 — Database no Supabase (10 min)

1. Criar conta em supabase.com
2. New Project → escolher região **Frankfurt (EU)** (obrigatório para RGPD)
3. Anotar a connection string:
   `postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres`
4. Converter para asyncpg:
   `postgresql+asyncpg://postgres:[password]@db.[ref].supabase.co:5432/postgres`

---

## PASSO 3 — Email no Resend (5 min)

1. Criar conta em resend.com
2. Add Domain → `pontevpn.com`
3. Adicionar registos DNS indicados (TXT e MX) no Cloudflare
4. Aguardar verificação (~5 min)
5. API Keys → Create API Key → copiar

---

## PASSO 4 — Stripe (20 min)

1. Criar conta em stripe.com
2. Ativar conta com os seus dados (NIF, morada em PT)
3. Criar produtos:

   **No Dashboard Stripe → Produtos → Novo Produto:**

   ```
   Produto: PonteVPN Pro
   ├── Preço 1: €7,99/mês (mensal)     → copiar Price ID
   └── Preço 2: €63,99/ano (anual)     → copiar Price ID

   Produto: PonteVPN Business
   └── Preço: €19,99/mês               → copiar Price ID
   ```

4. Ativar Stripe Tax:
   - Configurações → Tax → Ativar
   - Adicionar Portugal como país de origem

5. Criar Webhook:
   - Developers → Webhooks → Add endpoint
   - URL: `https://api.pontevpn.com/payments/webhook`
   - Eventos a escutar:
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_failed`
   - Copiar o Signing Secret (whsec_...)

---

## PASSO 5 — Servidor VPN no Hetzner (20 min)

1. Criar conta em hetzner.com
2. New Server:
   - Location: **Falkenstein (Alemanha)** para EU, ou **Gravataí (Brasil)** para BR
   - OS: Ubuntu 22.04
   - Tipo: CX22 (€4,51/mês)
   - Ativar backups
3. SSH para o servidor:
   ```bash
   ssh root@[IP_DO_SERVIDOR]
   ```
4. Executar o script de setup:
   ```bash
   curl -O https://raw.githubusercontent.com/[seu-repo]/main/infrastructure/setup-vpn-server.sh
   bash setup-vpn-server.sh "SEU_SECRET_AQUI"
   ```
5. Copiar os valores mostrados no final:
   - IP do servidor
   - Chave pública WireGuard
   - URL do agente

---

## PASSO 6 — Backend no Railway (15 min)

1. Criar conta em railway.app
2. New Project → Deploy from GitHub Repo
3. Selecionar o repositório → pasta `/backend`
4. Em Variables, adicionar todas as variáveis do `.env.example`:
   ```
   DATABASE_URL=postgresql+asyncpg://...
   SECRET_KEY=[gerar com: openssl rand -hex 32]
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_PRICE_PRO_MONTHLY=price_...
   STRIPE_PRICE_PRO_YEARLY=price_...
   STRIPE_PRICE_BUSINESS=price_...
   RESEND_API_KEY=re_...
   APP_URL=https://pontevpn.com
   API_URL=https://api.pontevpn.com
   VPN_SERVERS_API_SECRET=[mesmo secret do passo 5]
   ```
5. Em Settings → Domains → Custom Domain: `api.pontevpn.com`
6. Deploy automático ao push para main

---

## PASSO 7 — Adicionar Servidor VPN na Base de Dados

Após o backend estar no ar, inserir o servidor diretamente no Supabase:

```sql
INSERT INTO servers (name, country, country_code, city, ip, wg_port, wg_public_key, agent_url, capacity, min_plan)
VALUES (
  'Brasil - São Paulo',
  'Brasil',
  'BR',
  'São Paulo',
  '[IP_DO_SERVIDOR]',
  51820,
  '[CHAVE_PUBLICA_WG]',
  'http://[IP_DO_SERVIDOR]:8080',
  500,
  'free'
);
```

---

## PASSO 8 — Frontend no Vercel (10 min)

1. Criar conta em vercel.com
2. New Project → Import from GitHub → pasta `/frontend`
3. Em Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://api.pontevpn.com
   ```
4. Deploy
5. Settings → Domains → Add: `pontevpn.com` e `www.pontevpn.com`

---

## PASSO 9 — Verificação Final

Testar antes de anunciar:
```
[ ] https://pontevpn.com carrega (landing page)
[ ] https://pontevpn.com/auth/register — criar conta de teste
[ ] Email de verificação chegou
[ ] Login funciona
[ ] Dashboard carrega
[ ] Lista de servidores aparece
[ ] Gerar config → ficheiro .conf descarrega
[ ] Importar .conf no WireGuard → conectar ao servidor VPN
[ ] Verificar IP em ipinfo.io → deve mostrar IP do servidor
[ ] Stripe test mode → testar pagamento com cartão 4242 4242 4242 4242
[ ] Após pagamento, plano muda para Pro no dashboard
```

---

## MANUTENÇÃO MENSAL

```bash
# Verificar estado dos servidores VPN
ssh root@[IP_SERVIDOR] "wg show wg0"
systemctl status pontevpn-agent

# Ver logs do backend
railway logs --tail

# Backups Supabase → automáticos no plano Pro
# Backups Hetzner → ativar no painel (€0,90/mês)
```

---

## CUSTO REAL MENSAL (após lançamento)

```
Vercel (frontend):        €0
Railway (backend):        €5
Supabase (database):      €0 (grátis até 500MB)
Servidor VPN BR:          €5 (Vultr São Paulo)
Servidor VPN EU:          €5 (Hetzner Falkenstein)
Resend (email):           €0 (até 3.000/mês)
Cloudflare:               €0
Domínio (amortizado):     €1
Software de faturação:    €15 (InvoiceExpress)
─────────────────────────────
TOTAL:                    ~€31/mês

Break-even: 4 clientes Pro (4 × €7,99 = €31,96)
```
