import requests
from requests.auth import HTTPBasicAuth
from decouple import config

# Tus variables de configuración
SHAREPOINT_SITE_URL = config("SHAREPOINT_SITE_URL")
SHAREPOINT_USERNAME = config("SHAREPOINT_USERNAME")
SHAREPOINT_PASSWORD = config("SHAREPOINT_PASSWORD")


def test_basic_auth():
    """Probar autenticación básica"""
    try:
        auth = HTTPBasicAuth(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD)
        response = requests.get(f"{SHAREPOINT_SITE_URL}/_api/web", auth=auth, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Error en basic auth: {e}")
        return False


def test_saml_token():
    """Probar con office365 (tu método actual)"""
    try:
        from office365.runtime.auth.authentication_context import AuthenticationContext
        from office365.sharepoint.client_context import ClientContext

        ctx_auth = AuthenticationContext(SHAREPOINT_SITE_URL)
        result = ctx_auth.acquire_token_for_user(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD)
        if result:
            ctx = ClientContext(SHAREPOINT_SITE_URL, ctx_auth)
            web = ctx.web
            ctx.load(web)
            ctx.execute_query()
            return True
        return False
    except Exception as e:
        print(f"Error en SAML: {e}")
        return False


def test_legacy_auth():
    """Probar endpoint legacy"""
    try:
        legacy_url = f"{SHAREPOINT_SITE_URL}/_vti_bin/client.svc"
        auth = HTTPBasicAuth(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD)
        response = requests.get(legacy_url, auth=auth, timeout=30)
        return response.status_code in [200, 401]  # 401 también indica que llega al endpoint
    except Exception as e:
        print(f"Error en legacy: {e}")
        return False


def debug_authentication_timeline():
    """Verificar qué métodos funcionan"""
    print("Probando diferentes métodos de autenticación...\n")

    methods = [
        ("Basic Auth", test_basic_auth),
        ("SAML Token", test_saml_token),
        ("Legacy Auth", test_legacy_auth)
    ]

    for method_name, test_func in methods:
        try:
            result = test_func()
            status = "✓ Funciona" if result else "✗ Falla"
            print(f"{method_name}: {status}")
        except Exception as e:
            print(f"{method_name}: ✗ Error - {str(e)[:100]}")

    print("\n" + "=" * 50)
    print("Si todos fallan, definitivamente necesitas App Registration")


if __name__ == "__main__":
    debug_authentication_timeline()