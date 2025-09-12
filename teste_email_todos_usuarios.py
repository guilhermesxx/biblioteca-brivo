#!/usr/bin/env python
"""
📧 TESTE DE EMAIL PARA TODOS OS USUÁRIOS
Script para enviar email de teste para todos os usuários ativos do sistema
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from brivo.models import Usuario
from brivo.utils import enviar_email_manual

def enviar_teste_para_todos():
    """
    Envia email de teste para todos os usuários ativos
    """
    print("🚀 Iniciando envio de email de teste para todos os usuários...")
    
    # Buscar todos os usuários ativos
    usuarios = Usuario.objects.filter(ativo=True)
    
    if not usuarios.exists():
        print("❌ Nenhum usuário ativo encontrado!")
        return
    
    print(f"📊 Encontrados {usuarios.count()} usuários ativos")
    
    # Template do email de teste
    assunto = "📧 Teste do Sistema de Emails - Biblioteca Brivo"
    
    emails_enviados = 0
    emails_falharam = 0
    
    for usuario in usuarios:
        # Mensagem personalizada para cada usuário
        mensagem = f"""
Olá {usuario.nome}!

Este é um EMAIL DE TESTE do sistema da Biblioteca Brivo.

📧 INFORMAÇÕES DO TESTE:
• Data: {django.utils.timezone.now().strftime('%d/%m/%Y às %H:%M')}
• Destinatário: {usuario.email}
• Tipo de usuário: {usuario.get_tipo_display()}
• RA: {usuario.ra}
• Turma: {usuario.turma}

✅ SE VOCÊ RECEBEU ESTE EMAIL:
O sistema de notificações automáticas está funcionando perfeitamente!

🔔 VOCÊ RECEBERÁ EMAILS AUTOMÁTICOS PARA:
• Confirmação de cadastro
• Confirmação de reservas
• Confirmação de empréstimos
• Lembretes de devolução
• Notificações da fila de espera
• Novidades da biblioteca

📚 SISTEMA BIBLIOTECA BRIVO
Este é apenas um teste. Nenhuma ação é necessária.

---
Equipe da Biblioteca Brivo
Sistema de Notificações Automáticas
"""
        
        # Tentar enviar email
        try:
            sucesso = enviar_email_manual(
                destinatario_email=usuario.email,
                assunto_personalizado=assunto,
                mensagem_personalizada=mensagem,
                remetente_usuario=None
            )
            
            if sucesso:
                emails_enviados += 1
                print(f"✅ Email enviado para: {usuario.nome} ({usuario.email})")
            else:
                emails_falharam += 1
                print(f"❌ Falha ao enviar para: {usuario.nome} ({usuario.email})")
                
        except Exception as e:
            emails_falharam += 1
            print(f"❌ Erro ao enviar para {usuario.nome}: {str(e)}")
    
    # Relatório final
    print("\n" + "="*50)
    print("📊 RELATÓRIO FINAL DO TESTE")
    print("="*50)
    print(f"👥 Total de usuários: {usuarios.count()}")
    print(f"✅ Emails enviados: {emails_enviados}")
    print(f"❌ Emails falharam: {emails_falharam}")
    print(f"📈 Taxa de sucesso: {(emails_enviados/usuarios.count()*100):.1f}%")
    print("="*50)
    
    if emails_enviados > 0:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("📧 Verifique as caixas de email dos usuários")
    else:
        print("⚠️ NENHUM EMAIL FOI ENVIADO!")
        print("🔧 Verifique as configurações de SMTP")

if __name__ == "__main__":
    try:
        enviar_teste_para_todos()
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro durante o teste: {str(e)}")