#!/usr/bin/env python
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from django.core.mail import send_mail

def teste_email():
    try:
        print("Testando envio de email...")
        
        resultado = send_mail(
            subject='Teste de Email - Biblioteca Brivo',
            message='Este é um teste simples do sistema de email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['brivo1652@gmail.com'],
            fail_silently=False,
        )
        
        if resultado:
            print("✅ Email enviado com sucesso!")
        else:
            print("❌ Falha no envio do email")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    teste_email()