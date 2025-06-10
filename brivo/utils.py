# brivo/utils.py

from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta, date
from django.utils.timezone import now

from .models import Emprestimo  # ok ✅
# brivo/utils.py

from datetime import timedelta
from django.utils import timezone
from .models import Reserva


def enviar_avisos_reserva_expirando():
    hoje = timezone.now().date()
    dia_seguinte = hoje + timedelta(days=1)

    reservas = Reserva.objects.filter(
        status='aguardando_confirmacao',
        data_reserva__date=hoje - timedelta(days=1)  # supondo que validade = 2 dias
    )

    for reserva in reservas:
        assunto = "Sua reserva está prestes a expirar"
        mensagem = f"""
Olá, {reserva.aluno.nome}!

Você fez uma reserva do livro "{reserva.livro.titulo}" e ela vai expirar amanhã.

Caso ainda queira o livro, confirme o empréstimo no sistema o quanto antes.

Se não for confirmada, ela será liberada para o próximo da fila.

Atenciosamente,  
Biblioteca Escolar
"""
        enviar_email(destinatario=reserva.aluno.email, assunto=assunto, mensagem=mensagem)


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

# brivo/utils.py

def notificar_primeiro_da_fila(livro):
    from .models import Reserva  # evitar import circular

    reserva = Reserva.objects.filter(livro=livro, notificado=False).order_by('data_reserva').first()

    if reserva:
        usuario = reserva.usuario
        assunto = "📚 Livro disponível para retirada"
        mensagem = f"Olá {usuario.nome},\n\nO livro '{livro.titulo}' que você reservou está disponível para retirada.\n\nRetire-o o quanto antes para garantir seu empréstimo. 😉\n\nSistema de Biblioteca Escolar"

        enviar_email(usuario.email, assunto, mensagem)

        reserva.notificado = True
        reserva.save()
