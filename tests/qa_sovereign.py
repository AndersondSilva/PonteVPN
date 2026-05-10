import os
import httpx
import pytest
import subprocess
from playwright.sync_api import sync_playwright

# Configurações de Produção
FRONTEND_URL = "https://ponte-vpn.vercel.app"
BACKEND_URL = "https://pontevpn-production.up.railway.app"

def test_backend_health():
    """Verifica se o backend está vivo e respondendo."""
    print(f"\n[QA] Testando saude do Backend: {BACKEND_URL}")
    try:
        response = httpx.get(f"{BACKEND_URL}/health", timeout=10)
        assert response.status_code == 200
        assert response.json().get("status") == "ok"
        print(" SUCCESS: Backend Saudavel.")
    except Exception as e:
        pytest.fail(f"Backend Offline ou com erro: {e}")

def test_frontend_rendering():
    """Verifica se o frontend carrega e renderiza os elementos principais."""
    print(f"\n[QA] Testando renderizacao do Frontend: {FRONTEND_URL}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(FRONTEND_URL, wait_until="networkidle")
            
            # Verificar título
            assert "PonteVPN" in page.title()
            
            # Verificar se o Hero Section está visível
            hero_text = page.locator("h1").inner_text()
            assert len(hero_text) > 0
            
            # Verificar se o seletor de idioma existe
            lang_toggle = page.locator("button:has-text('PT'), button:has-text('EN')")
            assert lang_toggle.count() > 0
            
            print(" SUCCESS: Frontend Renderizado com sucesso.")
        except Exception as e:
            pytest.fail(f"Erro ao renderizar Frontend: {e}")
        finally:
            browser.close()

def test_security_audit():
    """Executa uma auditoria básica de segurança (Bandit)."""
    print("\n[SECURITY] Iniciando Auditoria de Codigo...")
    backend_path = r"e:\Projects\VPN\pontevpn\backend"
    result = subprocess.run(["python", "-m", "bandit", "-r", "."], cwd=backend_path, capture_output=True, text=True)
    
    # Verificar se há vulnerabilidades críticas (High severity)
    if "Severity: High" in result.stdout:
        print(" [!] VULNERABILIDADE CRITICA DETECTADA!")
        print(result.stdout)
        pytest.fail("Security Audit Failed: High Severity issues found.")
    else:
        print(" SUCCESS: Nenhuma vulnerabilidade critica detectada no codigo.")

if __name__ == "__main__":
    print("==========================================")
    print("   MANDATORY QA & SECURITY PROTOCOL      ")
    print("==========================================")
    
    # Rodar os testes via pytest
    pytest.main([__file__, "-v", "-s"])
