# brivo/utils.py

from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta, date
from django.utils.timezone import now

from .models import Emprestimo  # ok ✅


def enviar_email(destinatario, assunto, mensagem):
    send_mail(
        subject=assunto,
        message=mensagem,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[destinatario],
        fail_silently=False,
    )


def enviar_lembretes_de_devolucao():
    hoje = date.today()
    amanha = hoje + timedelta(days=1)

    emprestimos_vencendo = Emprestimo.objects.filter(data_devolucao=amanha, devolvido=False)

    for emprestimo in emprestimos_vencendo:
        usuario = emprestimo.usuario
        livro = emprestimo.livro

        assunto = "📚 Lembrete: Devolução do livro amanhã!"
        mensagem = f"Olá {usuario.nome},\n\nEste é um lembrete de que o livro '{livro.titulo}' deverá ser devolvido até amanhã ({emprestimo.data_devolucao}).\n\nPor favor, evite atrasos 😊.\n\nSistema de Biblioteca Escolar"

        enviar_email(usuario.email, assunto, mensagem)
