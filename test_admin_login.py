#!/usr/bin/env python
"""
🧪 TESTE DE LOGIN DOS ADMINISTRADORES
Testa se os logins com username funcionam corretamente
"""
import os
import sys
import django
import requests
import json

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from brivo.models import Usuario
from django.contrib.auth import authenticate

def test_django_authentication():
    """Testa autenticação diretamente no Django"""
    print("TESTE DE AUTENTICACAO DJANGO")
    print("=" * 40)
    
    # Testa os 3 administradores
    test_users = [
        {'username': 'adminbrivo1', 'password': 'Brivo2025@'},
        {'username': 'adminbrivo2', 'password': 'Brivo2025@'},
        {'username': 'adminbrivo3', 'password': 'Brivo2025@'}
    ]
    
    for test_user in test_users:
        username = test_user['username']
        password = test_user['password']
        
        print(f"Testando: {username}")
        
        # Testa autenticação Django
        user = authenticate(username=username, password=password)
        if user:
            print(f"  OK Django Auth: OK")
            print(f"     Nome: {user.nome}")
            print(f"     Tipo: {user.tipo}")
            print(f"     Ativo: {user.is_active}")
        else:
            print(f"  ERRO Django Auth: FALHOU")
        
        print()

def test_api_login():
    """Testa login via API"""
    print("TESTE DE LOGIN VIA API")
    print("=" * 40)
    
    # URL da API (ajuste conforme necessário)
    api_url = "http://127.0.0.1:8000/api/token/"
    
    # Testa os 3 administradores
    test_users = [
        {'username': 'adminbrivo1', 'password': 'Brivo2025@'},
        {'username': 'adminbrivo2', 'password': 'Brivo2025@'},
        {'username': 'adminbrivo3', 'password': 'Brivo2025@'}
    ]
    
    for test_user in test_users:
        username = test_user['username']
        password = test_user['password']
        
        print(f"Testando API: {username}")
        
        # Dados para enviar
        data = {
            'email': username,  # Usando campo 'email' mas enviando username
            'password': password,
            'tipo': 'admin'
        }
        
        try:
            response = requests.post(api_url, json=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  OK API Login: OK")
                print(f"     Token: {result.get('access', 'N/A')[:20]}...")
                print(f"     User: {result.get('user', {}).get('nome', 'N/A')}")
            else:
                print(f"  ERRO API Login: FALHOU")
                print(f"     Status: {response.status_code}")
                print(f"     Erro: {response.text}")
        
        except requests.exceptions.RequestException as e:
            print(f"  AVISO API nao disponivel: {e}")
        
        print()

def main():
    print("TESTE COMPLETO DE LOGIN ADMINISTRADORES")
    print("=" * 50)
    print()
    
    # Verifica se os usuários existem
    print("VERIFICANDO USUARIOS NO BANCO:")
    print("-" * 30)
    
    for username in ['adminbrivo1', 'adminbrivo2', 'adminbrivo3']:
        try:
            user = Usuario.objects.get(username=username)
            print(f"OK {username}: {user.nome} ({user.tipo})")
        except Usuario.DoesNotExist:
            print(f"ERRO {username}: NAO ENCONTRADO")
    
    print()
    
    # Testa autenticação Django
    test_django_authentication()
    
    # Testa API (se servidor estiver rodando)
    test_api_login()
    
    print("TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()