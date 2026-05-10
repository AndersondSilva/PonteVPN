import resend
from app.config import settings

resend.api_key = settings.RESEND_API_KEY


async def send_verification_email(to: str, token: str):
    url = f"{settings.APP_URL}/auth/verify?token={token}"
    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": to,
        "subject": "Confirme o seu email — PonteVPN",
        "html": f"""
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto">
          <h2 style="color:#1E3A5F">Bem-vindo à PonteVPN!</h2>
          <p>Clique no botão abaixo para confirmar o seu email:</p>
          <a href="{url}" style="display:inline-block;padding:12px 24px;
             background:#00B86B;color:#fff;border-radius:8px;
             text-decoration:none;font-weight:bold">
            Confirmar Email
          </a>
          <p style="color:#666;font-size:13px;margin-top:24px">
            Se não criou uma conta, ignore este email.
          </p>
        </div>
        """,
    })


async def send_welcome_email(to: str):
    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": to,
        "subject": "A sua conta PonteVPN está ativa!",
        "html": f"""
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto">
          <h2 style="color:#1E3A5F">Tudo pronto!</h2>
          <p>A sua conta está ativa. Aceda ao painel para descarregar
             a sua configuração VPN.</p>
          <a href="{settings.APP_URL}/dashboard" style="display:inline-block;
             padding:12px 24px;background:#00B86B;color:#fff;border-radius:8px;
             text-decoration:none;font-weight:bold">
            Ir para o Painel
          </a>
        </div>
        """,
    })


async def send_payment_failed_email(to: str):
    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": to,
        "subject": "Problema com o seu pagamento — PonteVPN",
        "html": f"""
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto">
          <h2 style="color:#c0392b">Pagamento não processado</h2>
          <p>Não conseguimos processar o seu pagamento. Por favor,
             atualize os dados do cartão para manter o acesso.</p>
          <a href="{settings.APP_URL}/dashboard/billing" style="display:inline-block;
             padding:12px 24px;background:#1E3A5F;color:#fff;border-radius:8px;
             text-decoration:none;font-weight:bold">
            Atualizar Cartão
          </a>
        </div>
        """,
    })
