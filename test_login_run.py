import os
import django

# Configura o ambiente Django para rodar scripts externos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biblioteca.settings")  # Ajuste para o nome do seu settings.py (sem .py)
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from brivo.models import Usuario

def tentar_login(email, senha, tipo_esperado):
    print(f"\n🔐 Testando login para {email} como tipo '{tipo_esperado}'...")

    usuario = authenticate(email=email, password=senha)
    if not usuario:
        print("❌ Falha ao autenticar: email ou senha incorretos.")
        return

    if not usuario.is_active:
        print("❌ Usuário está inativo.")
        return

    if usuario.tipo != tipo_esperado:
        print(f"❌ Tipo incorreto! Esperado: {tipo_esperado}, real: {usuario.tipo}")
        return

    refresh = RefreshToken.for_user(usuario)
    print("✅ Login bem-sucedido.")
    print("🔑 Access Token:", str(refresh.access_token))
    print("🔄 Refresh Token:", str(refresh))
    print("👤 Tipo do usuário:", usuario.tipo)

# Testes
tentar_login('guilherme1920x@gmail.com', 'brito@123', 'admin')
tentar_login('bolsominion1@gmail.com', 'brito@123', 'professor')
tentar_login('lula11@gmail.com', 'brito@123', 'aluno')