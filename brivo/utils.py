from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta, date
from django.utils.timezone import now # Importado 'now' diretamente para uso
import logging

# Importações de modelos
from .models import Emprestimo, Reserva, HistoricoAcao, AlertaSistema, Usuario

# Configura o logger
logger = logging.getLogger(__name__)

def registrar_acao(usuario, objeto, acao, descricao=''):
    """
    Registra uma ação no histórico do sistema.
    """
    try:
        HistoricoAcao.objects.create(
            usuario=usuario,
            objeto_tipo=type(objeto).__name__,
            objeto_id=objeto.id,
            acao=acao,
            descricao=descricao
        )
    except Exception as e:
        logger.error(f"Erro ao registrar ação para o objeto {objeto.__class__.__name__} (ID: {objeto.id}): {e}")


def enviar_email(destinatario, assunto, mensagem):
    """
    Envia um e-mail.
    """
    try:
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False, # Define como False para levantar exceções em caso de falha
        )
        logger.info(f"E-mail enviado para {destinatario} com assunto: {assunto}")
        return True
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail para {destinatario} (Assunto: {assunto}): {e}")
        return False


def enviar_lembretes_de_devolucao():
    """
    Envia lembretes de devolução para empréstimos que vencem amanhã.
    """
    hoje = date.today()
    amanha = hoje + timedelta(days=1)

    # CORREÇÃO: Usar __date para comparar apenas a parte da data do DateTimeField
    emprestimos_vencendo = Emprestimo.objects.filter(data_devolucao__date=amanha, devolvido=False)

    for emprestimo in emprestimos_vencendo:
        usuario = emprestimo.usuario
        livro = emprestimo.livro

        assunto = "📚 Lembrete: Devolução do livro amanhã!"
        mensagem = f"Olá {usuario.nome},\n\nEste é um lembrete de que o livro '{livro.titulo}' deverá ser devolvido até amanhã ({emprestimo.data_devolucao.strftime('%d/%m/%Y')}).\n\nPor favor, evite atrasos 😊.\n\nSistema de Biblioteca Escolar"

        enviar_email(usuario.email, assunto, mensagem)
        registrar_acao(None, emprestimo, 'NOTIFICACAO', descricao=f'Lembrete de devolução enviado para {usuario.nome} sobre o livro {livro.titulo}.')


def enviar_avisos_reserva_expirando():
    """
    Envia avisos para reservas que estão prestes a expirar.
    """
    # CORREÇÃO: Usar 'now()' diretamente, pois 'timezone' não é o objeto importado.
    hoje = now().date()
    # Supondo que a validade da reserva é de 2 dias e o aviso é enviado no dia anterior à expiração
    # Ajuste esta lógica conforme a regra de negócio da validade da reserva
    reservas = Reserva.objects.filter(
        status='aguardando_retirada', # Status mais apropriado para reservas aguardando retirada
        data_retirada_prevista__lte=hoje + timedelta(days=1), # Exemplo: Avisar se a retirada é até amanhã
        notificado_em__isnull=True # Para evitar enviar múltiplos avisos
    ).exclude(status__in=['expirada', 'cancelada', 'concluida']) # Excluir reservas já finalizadas

    for reserva in reservas:
        assunto = "Sua reserva está prestes a expirar"
        mensagem = f"""
Olá, {reserva.aluno.nome}!

Você fez uma reserva do livro "{reserva.livro.titulo}" e a data prevista para retirada é {reserva.data_retirada_prevista.strftime('%d/%m/%Y')}. Sua reserva vai expirar em breve se não for retirada.

Caso ainda queira o livro, retire-o no sistema o quanto antes.

Se não for retirada, ela será liberada para o próximo da fila.

Atenciosamente,
Biblioteca Escolar
"""
        if enviar_email(destinatario=reserva.aluno.email, assunto=assunto, mensagem=mensagem):
            # Marca a reserva como notificada para evitar reenvios
            reserva.notificado_em = now()
            reserva.save(update_fields=['notificado_em'])
            registrar_acao(None, reserva, 'NOTIFICACAO', descricao=f'Aviso de reserva expirando enviado para {reserva.aluno.nome} sobre o livro {reserva.livro.titulo}.')
        else:
            logger.warning(f"Falha ao enviar e-mail de aviso de reserva expirando para {reserva.aluno.email} (Reserva: {reserva.id}).")


def notificar_primeiro_da_fila(livro):
    """
    Notifica o próximo usuário na fila de espera por um livro.
    """
    reserva = Reserva.objects.filter(
        livro=livro,
        status='na_fila' # Apenas reservas que estão na fila
    ).order_by('data_reserva').first() # Pega o mais antigo na fila

    if reserva:
        usuario = reserva.aluno # O campo é 'aluno' no modelo Reserva
        assunto = "📚 Livro disponível para retirada"
        mensagem = f"Olá {usuario.nome},\n\nO livro '{livro.titulo}' que você reservou está disponível para retirada.\n\nPor favor, acesse o sistema para agendar a retirada em até 24 horas. Caso contrário, sua reserva poderá ser cancelada e o livro passará para o próximo da fila. 😉\n\nSistema de Biblioteca Escolar"

        if enviar_email(usuario.email, assunto, mensagem):
            reserva.notificado_em = now() # Atualiza o campo notificado_em com now()
            # O status da reserva permanece 'na_fila' ou pode ser alterado para 'aguardando_retirada'
            # se a notificação implica que o livro está pronto para ser retirado.
            # Se a lógica é que o usuário precisa AGENDAR a retirada, 'na_fila' ainda faz sentido.
            # Se a notificação significa que ele PODE retirar, então 'aguardando_retirada' é melhor.
            # Pelo texto do e-mail, parece que ele PODE retirar.
            reserva.status = 'aguardando_retirada' # Muda o status para aguardando retirada
            reserva.save()
            registrar_acao(None, reserva, 'NOTIFICACAO', descricao=f'Primeiro da fila notificado: {usuario.nome} sobre o livro {livro.titulo}.')
        else:
            logger.error(f"Não foi possível notificar o primeiro da fila para o livro {livro.titulo}.")


def enviar_notificacao_alerta_publico(alerta_id):
    """
    Envia e-mail de notificação para todos os usuários elegíveis (alunos e professores)
    quando um AlertaSistema público é criado ou atualizado.
    """
    try:
        alerta = AlertaSistema.objects.get(id=alerta_id)
    except AlertaSistema.DoesNotExist:
        logger.error(f"AlertaSistema com ID {alerta_id} não encontrado para envio de notificação.")
        return

    # Só envia se o alerta for público e ainda não tiver sido enviado
    if alerta.visibilidade == 'publico' and not alerta.email_enviado:
        # Filtra usuários que são alunos ou professores e estão ativos
        # Exclui administradores, pois eles gerenciam os alertas
        usuarios_para_notificar = Usuario.objects.filter(
            ativo=True,
            tipo__in=['aluno', 'professor']
        )

        assunto = f"📢 Alerta da Biblioteca: {alerta.titulo}"
        mensagem = f"""
Olá!

A Biblioteca Escolar tem um novo alerta para você:

Título: {alerta.titulo}
Mensagem: {alerta.mensagem}

Tipo de Alerta: {alerta.get_tipo_display()}
Data de Publicação: {alerta.data_publicacao.strftime('%d/%m/%Y %H:%M')}
{'Expira em: ' + alerta.expira_em.strftime('%d/%m/%Y %H:%M') if alerta.expira_em else ''}

Por favor, verifique o sistema para mais detalhes.

Atenciosamente,
Sistema de Biblioteca Escolar
"""
        emails_enviados_com_sucesso = []
        for usuario in usuarios_para_notificar:
            if enviar_email(usuario.email, assunto, mensagem):
                emails_enviados_com_sucesso.append(usuario.email)
            else:
                logger.warning(f"Falha ao enviar e-mail de alerta para {usuario.email} (Alerta: {alerta.titulo}).")

        if emails_enviados_com_sucesso:
            alerta.email_enviado = True
            alerta.save(update_fields=['email_enviado']) # Salva apenas o campo modificado
            registrar_acao(None, alerta, 'NOTIFICACAO', descricao=f'E-mail de alerta público "{alerta.titulo}" enviado para {len(emails_enviados_com_sucesso)} usuários.')
            logger.info(f"Alerta '{alerta.titulo}' marcado como 'email_enviado=True'.")
        else:
            logger.warning(f"Nenhum e-mail enviado para o alerta '{alerta.titulo}'. O campo 'email_enviado' não foi atualizado.")
