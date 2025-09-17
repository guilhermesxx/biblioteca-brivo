#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from brivo.models import Usuario

def test_create_users():
    """Teste direto de criação de usuários"""
    
    usuarios_teste = [
        {
            'ra': 'ALU001',
            'nome': 'Aluno Teste',
            'email': 'aluno@teste.com',
            'turma': '3A',
            'tipo': 'aluno',
            'senha': '123456'
        },
        {
            'ra': 'PROF001',
            'nome': 'Professor Teste',
            'email': 'professor@teste.com',
            'turma': 'DOCENTE',
            'tipo': 'professor',
            'senha': '123456'
        },
        {
            'ra': 'ADM001',
            'nome': 'Admin Teste',
            'email': 'admin@teste.com',
            'turma': 'ADMIN',
            'tipo': 'admin',
            'senha': '123456'
        }
    ]
    
    for user_data in usuarios_teste:
        try:
            # Remover se já existe
            Usuario.objects.filter(email=user_data['email']).delete()
            
            # Criar usuário
            usuario = Usuario.objects.create_user(
                ra=user_data['ra'],
                nome=user_data['nome'],
                email=user_data['email'],
                turma=user_data['turma'],
                tipo=user_data['tipo'],
                password=user_data['senha']
            )
            print(f"✅ {user_data['tipo'].upper()}: {usuario.nome} criado com ID {usuario.id}")
            
        except Exception as e:
            print(f"❌ {user_data['tipo'].upper()}: Erro - {str(e)}")

if __name__ == '__main__':
    test_create_users()