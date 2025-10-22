#!/usr/bin/env python
"""
🚀 SCRIPT PARA CRIAR ADMINISTRADORES BRIVO
Cria 3 contas de administrador com username e senha
"""
import os
import sys
import django

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from brivo.models import Usuario

def create_admin_users():
    """Cria os 3 administradores do sistema"""
    
    admins_data = [
        {
            'username': 'adminbrivo1',
            'nome': 'Administrador Brivo 1',
            'password': 'Brivo2025@'
        },
        {
            'username': 'adminbrivo2', 
            'nome': 'Administrador Brivo 2',
            'password': 'Brivo2025@'
        },
        {
            'username': 'adminbrivo3',
            'nome': 'Administrador Brivo 3', 
            'password': 'Brivo2025@'
        }
    ]
    
    print("CRIANDO ADMINISTRADORES BRIVO")
    print("=" * 50)
    
    for admin_data in admins_data:
        username = admin_data['username']
        
        # Verifica se já existe
        if Usuario.objects.filter(username=username).exists():
            print(f"AVISO: {username} ja existe - pulando...")
            continue
        
        try:
            # Cria o administrador
            admin = Usuario.objects.create_user(
                username=username,
                nome=admin_data['nome'],
                tipo='admin',
                password=admin_data['password'],
                turma='ADM'
            )
            
            print(f"SUCESSO: {username} criado com sucesso!")
            print(f"   Nome: {admin.nome}")
            print(f"   Tipo: {admin.tipo}")
            print(f"   Staff: {admin.is_staff}")
            print(f"   Superuser: {admin.is_superuser}")
            print()
            
        except Exception as e:
            print(f"ERRO ao criar {username}: {e}")
    
    print("RESUMO DOS ADMINISTRADORES:")
    print("-" * 30)
    
    admins = Usuario.objects.filter(tipo='admin')
    for admin in admins:
        login_info = admin.username if admin.username else admin.email
        print(f"ADMIN: {admin.nome}")
        print(f"   Login: {login_info}")
        print(f"   Senha: Brivo2025@")
        print()
    
    print("INFORMACOES DE LOGIN:")
    print("- Username: adminbrivo1, adminbrivo2, adminbrivo3")
    print("- Senha: Brivo2025@")
    print("- Tipo: admin")
    print()
    print("Sistema pronto para uso!")

if __name__ == "__main__":
    create_admin_users()