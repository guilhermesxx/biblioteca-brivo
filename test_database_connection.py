#!/usr/bin/env python
"""
Teste para verificar em qual banco de dados está salvando
"""
import os
import sys
import django
from pathlib import Path

# Adiciona o diretório do projeto ao path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from django.db import connection
from django.conf import settings
from brivo.models import Usuario

def test_database_info():
    """Testa informações do banco de dados"""
    print("=" * 60)
    print("TESTE DE CONEXÃO COM BANCO DE DADOS")
    print("=" * 60)
    
    # Informações da configuração
    db_config = settings.DATABASES['default']
    print(f"Engine: {db_config['ENGINE']}")
    
    if 'NAME' in db_config:
        print(f"Nome/Arquivo: {db_config['NAME']}")
    
    if 'HOST' in db_config:
        print(f"Host: {db_config.get('HOST', 'N/A')}")
    
    if 'PORT' in db_config:
        print(f"Porta: {db_config.get('PORT', 'N/A')}")
    
    if 'USER' in db_config:
        print(f"Usuário: {db_config.get('USER', 'N/A')}")
    
    # Verifica se DATABASE_URL está definida
    database_url = os.environ.get('DATABASE_URL')
    print(f"DATABASE_URL definida: {'Sim' if database_url else 'Não'}")
    if database_url:
        print(f"DATABASE_URL: {database_url[:50]}...")
    
    print("\n" + "-" * 40)
    
    # Testa a conexão
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Conexão com banco estabelecida com sucesso!")
            
            # Informações específicas do banco
            if 'postgresql' in db_config['ENGINE']:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                print(f"PostgreSQL Version: {version}")
                print("🐘 USANDO POSTGRESQL")
            elif 'sqlite' in db_config['ENGINE']:
                cursor.execute("SELECT sqlite_version()")
                version = cursor.fetchone()[0]
                print(f"SQLite Version: {version}")
                print("📁 USANDO SQLITE LOCAL")
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
    
    print("\n" + "-" * 40)
    
    # Testa operação de escrita
    try:
        # Conta usuários existentes
        user_count = Usuario.objects.count()
        print(f"Usuários existentes: {user_count}")
        
        # Cria um usuário de teste
        test_user = Usuario.objects.create_user(
            username=f'test_db_{hash(str(os.getpid()))}',
            email='test@test.com',
            password='testpass123',
            nome='Teste Database'
        )
        print(f"✅ Usuário de teste criado: {test_user.username}")
        
        # Verifica se foi salvo
        saved_user = Usuario.objects.get(id=test_user.id)
        print(f"✅ Usuário recuperado: {saved_user.username}")
        
        # Remove o usuário de teste
        test_user.delete()
        print("✅ Usuário de teste removido")
        
        print("🎯 TESTE DE ESCRITA/LEITURA: SUCESSO!")
        
    except Exception as e:
        print(f"❌ Erro no teste de escrita: {e}")
    
    print("\n" + "=" * 60)
    
    # Resumo final
    if database_url:
        print("🌐 CONCLUSÃO: Usando PostgreSQL online (Render)")
    else:
        print("💻 CONCLUSÃO: Usando SQLite local")
    
    print("=" * 60)

if __name__ == '__main__':
    test_database_info()