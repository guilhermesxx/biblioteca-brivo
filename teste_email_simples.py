#!/usr/bin/env python
import os
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def teste_email():
    """
    Teste simples de envio de email
    """
    print("🧪 Iniciando teste de email...")
    print(f"📧 Usando email: {settings.EMAIL_HOST_USER}")
    print(f"🔐 Senha configurada: {'*' * len(settings.EMAIL_HOST_PASSWORD)}")
    
    # Email de teste
    destinatario = input("📮 Digite o email de destino: ")
    
    try:
        send_mail(
            subject='🧪 Teste - Sistema Biblioteca Brivo',
            message='''
Olá!

Este é um teste do sistema de emails da Biblioteca Brivo.

✅ Se você recebeu este email, a configuração está funcionando!

📧 Email enviado de: bibliotecabrivo@gmail.com
🕒 Data/Hora: Agora mesmo

Equipe da Biblioteca Brivo
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False,
        )
        print("✅ Email enviado com sucesso!")
        print(f"📬 Verifique a caixa de entrada de: {destinatario}")
        print("📋 Não esqueça de verificar a pasta de spam também!")
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {str(e)}")
        print("🔧 Verifique as configurações SMTP no settings.py")

if __name__ == "__main__":
    teste_email()