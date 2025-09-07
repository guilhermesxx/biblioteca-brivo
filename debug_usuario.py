#!/usr/bin/env python
import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from brivo.models import Usuario
from brivo.serializers import UsuarioSerializer

def test_validation_errors():
    # Buscar usuário existente
    usuario = Usuario.objects.first()
    if not usuario:
        print("Nenhum usuário encontrado")
        return
    
    print(f"Testando usuário: {usuario.nome} (ID: {usuario.id})")
    
    # Teste 1: Dados válidos
    dados_validos = {
        'nome': 'Nome Teste',
        'turma': 'A1'
    }
    
    serializer = UsuarioSerializer(usuario, data=dados_validos, partial=True)
    if serializer.is_valid():
        print("OK - Dados validos: OK")
    else:
        print("ERRO - Dados validos falharam:")
        print(json.dumps(serializer.errors, indent=2))
    
    # Teste 2: Email duplicado
    outro_usuario = Usuario.objects.exclude(id=usuario.id).first()
    if outro_usuario:
        dados_email_duplicado = {
            'email': outro_usuario.email
        }
        
        serializer = UsuarioSerializer(usuario, data=dados_email_duplicado, partial=True)
        if not serializer.is_valid():
            print("OK - Email duplicado detectado:")
            print(json.dumps(serializer.errors, indent=2))
        else:
            print("ERRO - Email duplicado nao foi detectado")
    
    # Teste 3: RA duplicado
    if outro_usuario:
        dados_ra_duplicado = {
            'ra': outro_usuario.ra
        }
        
        serializer = UsuarioSerializer(usuario, data=dados_ra_duplicado, partial=True)
        if not serializer.is_valid():
            print("OK - RA duplicado detectado:")
            print(json.dumps(serializer.errors, indent=2))
        else:
            print("ERRO - RA duplicado nao foi detectado")
    
    # Teste 4: Campos obrigatorios vazios
    dados_vazios = {
        'nome': '',
        'email': '',
        'ra': ''
    }
    
    serializer = UsuarioSerializer(usuario, data=dados_vazios, partial=True)
    if not serializer.is_valid():
        print("OK - Campos vazios detectados:")
        print(json.dumps(serializer.errors, indent=2))
    else:
        print("ERRO - Campos vazios nao foram detectados")

if __name__ == '__main__':
    test_validation_errors()