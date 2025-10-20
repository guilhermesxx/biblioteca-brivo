#!/usr/bin/env python
"""
Script para testar se o servidor Django está funcionando
"""
import requests
import sys

def test_server():
    base_url = "http://172.30.1.85:8000"
    
    print(f"🔍 Testando conexão com {base_url}")
    
    try:
        # Teste básico de conexão
        response = requests.get(f"{base_url}/api/", timeout=5)
        print(f"✅ Servidor respondeu: {response.status_code}")
        
        # Teste do endpoint de login
        login_response = requests.post(f"{base_url}/api/token/", 
                                     json={"email": "test", "password": "test"}, 
                                     timeout=5)
        print(f"✅ Endpoint de login acessível: {login_response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se que o Django está rodando em 172.30.1.85:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout na conexão")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    if test_server():
        print("\n🎉 Servidor está funcionando!")
        sys.exit(0)
    else:
        print("\n💡 Para iniciar o servidor:")
        print("   cd C:\\Users\\GuilhermeGoncalvesDa.AzureAD\\Documents\\GitHub\\biblioteca-brivo")
        print("   python manage.py runserver 0.0.0.0:8000")
        sys.exit(1)