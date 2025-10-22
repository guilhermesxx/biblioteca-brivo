#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from brivo.models import Usuario
from django.contrib.auth.hashers import make_password

def criar_admins_tcc():
    try:
        # Verificar se já existem
        if Usuario.objects.filter(username='testebrivo1').exists():
            print('ERRO: testebrivo1 ja existe!')
        else:
            # Criar testebrivo1
            admin1 = Usuario.objects.create(
                username='testebrivo1',
                nome='Teste Brivo 1',
                tipo='admin',
                password=make_password('brivo@adm1'),
                is_staff=True,
                is_superuser=True
            )
            print('OK: Conta testebrivo1 criada!')

        if Usuario.objects.filter(username='testebrivo2').exists():
            print('ERRO: testebrivo2 ja existe!')
        else:
            # Criar testebrivo2
            admin2 = Usuario.objects.create(
                username='testebrivo2',
                nome='Teste Brivo 2',
                tipo='admin',
                password=make_password('brivo@adm1'),
                is_staff=True,
                is_superuser=True
            )
            print('OK: Conta testebrivo2 criada!')

        print('')
        print('CONTAS PARA TCC:')
        print('Username: testebrivo1 | Senha: brivo@adm1')
        print('Username: testebrivo2 | Senha: brivo@adm1')
        print('')
        print('Contas criadas com sucesso para teste do TCC!')
        
    except Exception as e:
        print(f'ERRO: {e}')

if __name__ == '__main__':
    criar_admins_tcc()