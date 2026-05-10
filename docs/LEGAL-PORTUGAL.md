# Obrigações Legais — PonteVPN em Portugal
# Atualizado: Março 2026

> Este documento é informativo. Consulte um advogado português
> para validação formal antes de lançar o serviço.

---

## 1. ATIVIDADE COMERCIAL — REGISTO

### Opção A: Trabalhador Independente (mais simples para começar)

1. Aceder ao Portal das Finanças (portaldasfinancas.gov.pt)
2. Autenticar com NIF + senha
3. Menu: Serviços → Entregar → Início de Atividade
4. Código CAE: **62090** (Outras atividades de tecnologia de informação)
5. Regime IVA: Isenção até €13.500/ano (art. 53º CIVA)
   — Acima disso: IVA normal obrigatório (23% em Portugal)
6. Regime IRS: Simplificado (coeficiente 0,75 sobre receitas)

**Custo de registo:** €0 (gratuito no portal)

### Opção B: Lda. (para faturação > €50k/ano)

- Mínimo €1 de capital social
- Notário: ~€300-500
- Registo Comercial: ~€200
- Contabilista certificado: ~€150-300/mês (obrigatório para Lda.)

**Recomendação:** Comece como Trabalhador Independente.
Converta para Lda. quando o MRR ultrapassar €3.000/mês.

---

## 2. IVA (IMPOSTO SOBRE VALOR ACRESCENTADO)

### Clientes em Portugal
- Abaixo de €13.500/ano: isento de IVA
- Acima de €13.500/ano: cobrar 23% de IVA

### Clientes noutros países da UE (B2C — consumidores finais)
- Regra: cobrar IVA do país do cliente
- Solução: registar no **IVA OSS** (One-Stop Shop)
  → portal.oss.uat.ec.europa.eu
  → Declara e paga numa só declaração trimestral
  → O Stripe Tax trata automaticamente se ativar

### Clientes fora da UE (Brasil, EUA, etc.)
- Serviços digitais exportados: taxa 0% (isento)

**Ação imediata:** Ativar o Stripe Tax no dashboard Stripe.
O Stripe calcula e cobra o IVA correto automaticamente por país.

---

## 3. RGPD (REGULAMENTO GERAL DE PROTEÇÃO DE DADOS)

### Obrigações como operador de serviço digital na UE:

#### 3.1 Registo no CNPD (Comissão Nacional de Proteção de Dados)
- Website: cnpd.pt
- Registar as atividades de tratamento de dados
- Custo: gratuito
- Prazo: antes de recolher qualquer dado pessoal

#### 3.2 O que deve fazer:
- [ ] Publicar Política de Privacidade clara (template em docs/)
- [ ] Publicar Política de Cookies
- [ ] Implementar banner de consentimento de cookies
- [ ] Disponibilizar formulário de "Direito de eliminação" (direito ao esquecimento)
- [ ] Responder a pedidos de acesso a dados em 30 dias
- [ ] Informar utilizadores em caso de violação de dados em 72 horas

#### 3.3 O que NÃO pode fazer (RGPD + política no-logs):
- Vender dados de utilizadores a terceiros
- Partilhar dados com autoridades sem ordem judicial
- Guardar dados mais tempo do que o necessário

#### 3.4 Dados permitidos guardar (e por quanto tempo):
| Dado | Motivo | Retenção |
|------|--------|----------|
| Email | Gestão de conta | Enquanto conta ativa + 1 ano |
| Hash de password | Autenticação | Enquanto conta ativa |
| Dados de faturação | Obrigação fiscal | 10 anos (lei fiscal PT) |
| Chave pública WireGuard | Funcionamento do serviço | Enquanto config ativa |
| Bytes transferidos | Limite do plano Free | 90 dias |

#### 3.5 Dados PROIBIDOS de guardar:
- IPs de destino visitados
- Consultas DNS
- Histórico de navegação
- Timestamps de sessão individuais

---

## 4. LEGALIDADE DO SERVIÇO VPN

### Em Portugal:
**VPN é 100% legal em Portugal e na UE.**

Não existe qualquer lei portuguesa ou europeia que:
- Proíba a operação de serviços VPN
- Obrigue a guardar logs de tráfego para VPNs (ao contrário de ISPs)
- Limite o uso de criptografia

### Jurisprudência relevante:
- Diretiva ePrivacy (2002/58/CE) — protege privacidade das comunicações
- RGPD — reforça proteção de dados pessoais
- Carta dos Direitos Fundamentais da UE (art. 7º e 8º) — privacidade e proteção de dados

### Limites legais:
A PonteVPN **não pode** ser usada para:
- Atividades ilegais (deve constar nos Termos de Serviço)
- Partilha não autorizada de conteúdo protegido (pirataria)
- Spam ou ciberataques

**Como se proteger:** Os Termos de Serviço devem proibir explicitamente
o uso ilegal. Se seguir a política no-logs, não tem responsabilidade
pelos atos dos utilizadores (semelhante a um ISP).

---

## 5. FATURAÇÃO

### Obrigações:
- Emitir fatura eletrónica a cada pagamento
- Comunicar faturas ao sistema e-fatura (Autoridade Tributária)
- O Stripe emite recibos mas NÃO substitui a fatura portuguesa

### Solução prática:
Usar um programa de faturação certificado pela AT:
- **InvoiceExpress** (recomendado) — integra com Stripe via webhook
- **Moloni** — alternativa
- **PHC** — mais completo, para volumes maiores

Custo: ~€15-30/mês

---

## 6. TERMOS DE SERVIÇO — PONTOS OBRIGATÓRIOS (EU)

Pelo Direito do Consumidor da UE:
- [ ] Direito de arrependimento de 14 dias (mas pode excluir para serviços digitais usados imediatamente)
- [ ] Informação sobre cancelamento deve ser clara
- [ ] Preço total (com impostos) deve ser visível antes do pagamento
- [ ] Informação de contacto real (morada ou email)
- [ ] Lei aplicável (Portugal) e tribunal competente

---

## 7. CHECKLIST ANTES DE LANÇAR

**Registo:**
- [ ] Início de atividade nas Finanças
- [ ] Registo no CNPD

**Website:**
- [ ] Política de Privacidade publicada (PT + EN)
- [ ] Termos de Serviço publicados (PT + EN)
- [ ] Política de Cookies + banner de consentimento
- [ ] Morada/email de contacto visível no rodapé
- [ ] Indicação de conformidade com RGPD

**Pagamentos:**
- [ ] Stripe Tax ativado
- [ ] Software de faturação configurado (InvoiceExpress)
- [ ] Webhook Stripe → fatura automática configurado

**Operacional:**
- [ ] Política no-logs documentada e implementada
- [ ] Processo para pedidos de eliminação de dados
- [ ] Email de contacto para questões legais: legal@pontevpn.com

---

## 8. CONTACTOS ÚTEIS

| Entidade | Website | Telefone |
|----------|---------|----------|
| Finanças (AT) | portaldasfinancas.gov.pt | 217 206 707 |
| CNPD | cnpd.pt | 213 928 400 |
| IAPMEI (apoio a empresas) | iapmei.pt | — |
| Ordem dos Advogados | oa.pt | — |

---

**Custo mensal estimado para operar legalmente:**
- Contabilidade (opcional, trabalhador independente): €0-80/mês
- Software de faturação: €15-30/mês
- **Total mínimo: €15/mês**
