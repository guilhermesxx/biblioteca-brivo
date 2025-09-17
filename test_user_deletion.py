#!/usr/bin/env python3
"""
Script para testar a funcionalidade de exclusão de usuários
"""
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from brivo.models import Usuario, Emprestimo, Reserva, AlertaSistema

def test_user_deletion():
    print("=== TESTE DE EXCLUSÃO DE USUÁRIO ===")
    
    # Criar um usuário de teste
    try:
        test_user = Usuario.objects.create_user(
            ra="TEST123",
            nome="Usuário Teste",
            email="teste@exemplo.com",
            turma="TESTE",
            tipo="aluno",
            password="senha123"
        )
        print(f"✓ Usuário criado: {test_user.nome} (ID: {test_user.id})")
        
        # Verificar se o usuário existe
        user_exists = Usuario.objects.filter(id=test_user.id).exists()
        print(f"✓ Usuário existe no banco: {user_exists}")
        
        # Simular exclusão (hard delete)
        user_id = test_user.id
        user_name = test_user.nome
        test_user.delete()
        
        # Verificar se foi realmente excluído
        user_exists_after = Usuario.objects.filter(id=user_id).exists()
        print(f"✓ Usuário existe após exclusão: {user_exists_after}")
        
        if not user_exists_after:
            print(f"✅ SUCESSO: Usuário '{user_name}' foi excluído permanentemente do banco de dados")
        else:
            print(f"❌ ERRO: Usuário '{user_name}' ainda existe no banco de dados")
            
    except Exception as e:
        print(f"❌ ERRO durante o teste: {str(e)}")

def test_email_uniqueness():
    print("\n=== TESTE DE UNICIDADE DE EMAIL ===")
    
    try:
        # Tentar criar usuário com email que já existe
        existing_user = Usuario.objects.filter(email="teste@exemplo.com").first()
        if existing_user:
            print(f"❌ PROBLEMA: Email 'teste@exemplo.com' ainda existe no banco (usuário: {existing_user.nome})")
        else:
            print("✅ SUCESSO: Email 'teste@exemplo.com' não existe mais no banco")
            
        # Tentar criar novo usuário com o mesmo email
        new_user = Usuario.objects.create_user(
            ra="NEW123",
            nome="Novo Usuário",
            email="teste@exemplo.com",
            turma="NOVO",
            tipo="aluno",
            password="senha123"
        )
        print(f"✅ SUCESSO: Novo usuário criado com email reutilizado: {new_user.nome}")
        
        # Limpar o usuário de teste
        new_user.delete()
        print("✓ Usuário de teste limpo")
        
    except Exception as e:
        print(f"❌ ERRO durante teste de unicidade: {str(e)}")

if __name__ == "__main__":
    test_user_deletion()
    test_email_uniqueness()
    print("\n=== TESTE CONCLUÍDO ===")