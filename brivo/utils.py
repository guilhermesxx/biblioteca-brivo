from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta, date
from django.utils.timezone import now # Importado 'now' diretamente para uso
import logging

# Importações de modelos
from .models import Emprestimo, Reserva, HistoricoAcao, AlertaSistema, Usuario, Livro

# Importar templates de email configuráveis
from .email_templates import (
    EMAIL_BOAS_VINDAS, EMAIL_CONFIRMACAO_RESERVA, EMAIL_LEMBRETE_RETIRADA,
    EMAIL_RESERVA_CANCELADA, EMAIL_EMPRESTIMO_CONFIRMADO, EMAIL_LEMBRETE_DEVOLUCAO_3_DIAS,
    EMAIL_LIVRO_ATRASO, EMAIL_DEVOLUCAO_CONFIRMADA, EMAIL_ENTRADA_FILA,
    EMAIL_SUA_VEZ_FILA, EMAIL_NOVOS_LIVROS, EMAIL_RECOMENDACOES,
    EMAIL_RELATORIO_MENSAL, EMAIL_ALERTA_ADMIN, EMAIL_DICAS_LEITURA,
    EMAIL_CONVITE_EVENTO, NOME_ESCOLA, ASSINATURA_PADRAO, PRAZO_EMPRESTIMO_DIAS
)

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
    Envia um e-mail usando o backend configurado.
    """
    try:
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False,
        )
        logger.info(f"Email enviado para {destinatario}")
        return True
    except Exception as e:
        logger.error(f"Falha ao enviar email para {destinatario}: {str(e)}")
        return False


def enviar_lembretes_de_devolucao():
    """
    Envia lembretes de devolução para empréstimos que vencem amanhã.
    📧 USA O EMAIL PREDEFINIDO PARA LEMBRETE DE DEVOLUÇÃO
    """
    hoje = date.today()
    # Calcular data de devolução (15 dias após empréstimo)
    data_limite_emprestimo = hoje - timedelta(days=12)  # Empréstimos que vencem em 3 dias

    # Buscar empréstimos que vencem em 3 dias
    emprestimos_vencendo = Emprestimo.objects.filter(
        data_emprestimo__date=data_limite_emprestimo,
        devolvido=False
    )

    for emprestimo in emprestimos_vencendo:
        # 📧 USAR EMAIL PREDEFINIDO DE LEMBRETE 3 DIAS
        enviar_email_lembrete_devolucao_3_dias(emprestimo)
        registrar_acao(None, emprestimo, 'NOTIFICACAO', descricao=f'Lembrete de devolução enviado para {emprestimo.usuario.nome} sobre o livro {emprestimo.livro.titulo}.')


def enviar_avisos_reserva_expirando():
    """
    Envia avisos para reservas que estão prestes a expirar.
    📧 USA O EMAIL PREDEFINIDO PARA LEMBRETE DE RETIRADA
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
        # 📧 USAR EMAIL PREDEFINIDO DE LEMBRETE DE RETIRADA
        if enviar_email_lembrete_retirada(reserva):
            # Marca a reserva como notificada para evitar reenvios
            reserva.notificado_em = now()
            reserva.save(update_fields=['notificado_em'])
            registrar_acao(None, reserva, 'NOTIFICACAO', descricao=f'Aviso de reserva expirando enviado para {reserva.aluno.nome} sobre o livro {reserva.livro.titulo}.')
        else:
            logger.warning(f"Falha ao enviar e-mail de aviso de reserva expirando para {reserva.aluno.email} (Reserva: {reserva.id}).")


def notificar_primeiro_da_fila(livro):
    """
    Notifica o próximo usuário na fila de espera por um livro.
    📧 USA O EMAIL PREDEFINIDO PARA NOTIFICAÇÃO DA FILA
    """
    reserva = Reserva.objects.filter(
        livro=livro,
        status='na_fila' # Apenas reservas que estão na fila
    ).order_by('data_reserva').first() # Pega o mais antigo na fila

    if reserva:
        # 📧 USAR EMAIL PREDEFINIDO DE "SUA VEZ NA FILA"
        if enviar_email_sua_vez_fila(reserva):
            reserva.notificado_em = now() # Atualiza o campo notificado_em com now()
            # O status da reserva permanece 'na_fila' ou pode ser alterado para 'aguardando_retirada'
            # se a notificação implica que o livro está pronto para ser retirado.
            # Se a lógica é que o usuário precisa AGENDAR a retirada, 'na_fila' ainda faz sentido.
            # Se a notificação significa que ele PODE retirar, então 'aguardando_retirada' é melhor.
            # Pelo texto do e-mail, parece que ele PODE retirar.
            reserva.status = 'aguardando_retirada' # Muda o status para aguardando retirada
            reserva.save()
            registrar_acao(None, reserva, 'NOTIFICACAO', descricao=f'Primeiro da fila notificado: {reserva.aluno.nome} sobre o livro {livro.titulo}.')
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

        assunto = f"Alerta da Biblioteca: {alerta.titulo}"
        mensagem = f"""
Ola!

A Biblioteca Escolar tem um novo alerta para voce:

Titulo: {alerta.titulo}
Mensagem: {alerta.mensagem}

Tipo de Alerta: {alerta.get_tipo_display()}
Data de Publicacao: {alerta.data_publicacao.strftime('%d/%m/%Y %H:%M')}
{'Expira em: ' + alerta.expira_em.strftime('%d/%m/%Y %H:%M') if alerta.expira_em else ''}

Por favor, verifique o sistema para mais detalhes.

Atenciosamente,
Sistema de Biblioteca Escolar
"""
        emails_enviados_com_sucesso = []
        emails_falharam = []
        
        for usuario in usuarios_para_notificar:
            if enviar_email(usuario.email, assunto, mensagem):
                emails_enviados_com_sucesso.append(usuario.email)
            else:
                emails_falharam.append(usuario.email)
                logger.warning(f"Falha ao enviar e-mail de alerta para {usuario.email} (Alerta: {alerta.titulo}).")

        # Sempre marca como enviado para não bloquear o sistema
        total_usuarios = len(usuarios_para_notificar)
        alerta.email_enviado = True
        alerta.save(update_fields=['email_enviado'])
        
        if len(emails_enviados_com_sucesso) > 0:
            registrar_acao(None, alerta, 'NOTIFICACAO', 
                         descricao=f'E-mail de alerta público "{alerta.titulo}" enviado para {len(emails_enviados_com_sucesso)}/{total_usuarios} usuários.')
            logger.info(f"Alerta '{alerta.titulo}' processado. Sucesso: {len(emails_enviados_com_sucesso)}/{total_usuarios}")
        else:
            registrar_acao(None, alerta, 'NOTIFICACAO', 
                         descricao=f'Alerta público "{alerta.titulo}" criado (emails falharam por problema de conexão).')
            logger.warning(f"Alerta '{alerta.titulo}' criado mas emails falharam. Problema de conexão SMTP.")


# =============================================================================
# 📧 SISTEMA DE EMAILS AUTOMÁTICOS PREDEFINIDOS
# =============================================================================

# -----------------------------------------------------------------------------
# 🎯 1. AUTENTICAÇÃO E BOAS-VINDAS
# -----------------------------------------------------------------------------

def enviar_email_boas_vindas(usuario):
    """
    📝 Email de Boas-vindas (Novo Cadastro)
    Enviado quando um novo usuário é criado no sistema
    📧 TEMPLATE EDITÁVEL EM: email_templates.py -> EMAIL_BOAS_VINDAS
    """
    # USAR TEMPLATE CONFIGURÁVEL
    assunto = EMAIL_BOAS_VINDAS['assunto']
    mensagem = EMAIL_BOAS_VINDAS['template'].format(
        nome=usuario.nome,
        email=usuario.email,
        ra=usuario.ra,
        turma=usuario.turma,
        tipo=usuario.get_tipo_display()
    )
    
    if enviar_email(usuario.email, assunto, mensagem):
        registrar_acao(None, usuario, 'NOTIFICACAO', descricao=f'Email de boas-vindas enviado para {usuario.nome}')
        return True
    return False

# -----------------------------------------------------------------------------
# 📚 2. RESERVAS E AGENDAMENTOS
# -----------------------------------------------------------------------------

def enviar_email_confirmacao_reserva(reserva):
    """
    ✅ Confirmação de Reserva
    Enviado quando uma reserva é criada com sucesso
    📧 TEMPLATE EDITÁVEL EM: email_templates.py -> EMAIL_CONFIRMACAO_RESERVA
    """
    # USAR TEMPLATE CONFIGURÁVEL
    data_retirada = reserva.data_retirada_prevista.strftime('%d/%m/%Y') if reserva.data_retirada_prevista else 'A definir'
    hora_retirada = reserva.hora_retirada_prevista.strftime('%H:%M') if reserva.hora_retirada_prevista else 'A definir'
    
    assunto = EMAIL_CONFIRMACAO_RESERVA['assunto'].format(titulo=reserva.livro.titulo)
    mensagem = EMAIL_CONFIRMACAO_RESERVA['template'].format(
        nome=reserva.aluno.nome,
        titulo=reserva.livro.titulo,
        autor=reserva.livro.autor,
        data_retirada=data_retirada,
        hora_retirada=hora_retirada
    )
    
    if enviar_email(reserva.aluno.email, assunto, mensagem):
        registrar_acao(None, reserva, 'NOTIFICACAO', descricao=f'Email de confirmação de reserva enviado para {reserva.aluno.nome}')
        return True
    return False

def enviar_email_lembrete_retirada(reserva):
    """
    ⏰ Lembrete de Retirada (1 dia antes)
    Enviado 1 dia antes da data de retirada agendada
    """
    assunto = "⏰ Lembrete: Retire seu livro amanhã!"
    
    # TEMPLATE DE LEMBRETE DE RETIRADA - Editável aqui
    data_retirada = reserva.data_retirada_prevista.strftime('%d/%m/%Y')
    hora_retirada = reserva.hora_retirada_prevista.strftime('%H:%M')
    
    mensagem = f"""
Olá {reserva.aluno.nome},

Não esqueça! Amanhã é o dia de retirar seu livro reservado.

📚 \"{reserva.livro.titulo}\"
📅 Data: {data_retirada} às {hora_retirada}
📍 Local: Biblioteca da Escola

Não consegue comparecer? 
• Reagende pelo sistema
• Ou cancele a reserva

📱 Gerencie sua reserva no sistema!

Até amanhã!
Equipe da Biblioteca
"""
    
    if enviar_email(reserva.aluno.email, assunto, mensagem):
        registrar_acao(None, reserva, 'NOTIFICACAO', descricao=f'Email de lembrete de retirada enviado para {reserva.aluno.nome}')
        return True
    return False

def enviar_email_reserva_cancelada(reserva):
    """
    ❌ Reserva Cancelada
    Enviado quando uma reserva é cancelada
    """
    assunto = f"❌ Reserva Cancelada: \"{reserva.livro.titulo}\""
    
    # TEMPLATE DE RESERVA CANCELADA - Editável aqui
    data_seria_retirada = reserva.data_retirada_prevista.strftime('%d/%m/%Y') if reserva.data_retirada_prevista else 'Data não definida'
    
    mensagem = f"""
Olá {reserva.aluno.nome},

Sua reserva foi cancelada conforme solicitado.

📚 Livro: {reserva.livro.titulo}
📅 Data que seria retirada: {data_seria_retirada}

💡 Quer reservar novamente?
Acesse o sistema e faça uma nova reserva quando desejar.

📱 Explore mais livros no sistema!

Equipe da Biblioteca
"""
    
    if enviar_email(reserva.aluno.email, assunto, mensagem):
        registrar_acao(None, reserva, 'NOTIFICACAO', descricao=f'Email de cancelamento de reserva enviado para {reserva.aluno.nome}')
        return True
    return False

# -----------------------------------------------------------------------------
# 📖 3. EMPRÉSTIMOS
# -----------------------------------------------------------------------------

def enviar_email_emprestimo_confirmado(emprestimo):
    """
    🎉 Empréstimo Confirmado
    Enviado quando um empréstimo é registrado
    📧 TEMPLATE EDITÁVEL EM: email_templates.py -> EMAIL_EMPRESTIMO_CONFIRMADO
    """
    # USAR TEMPLATE CONFIGURÁVEL
    data_emprestimo = emprestimo.data_emprestimo.strftime('%d/%m/%Y')
    data_devolucao = (emprestimo.data_emprestimo + timedelta(days=PRAZO_EMPRESTIMO_DIAS)).strftime('%d/%m/%Y')
    
    assunto = EMAIL_EMPRESTIMO_CONFIRMADO['assunto'].format(titulo=emprestimo.livro.titulo)
    mensagem = EMAIL_EMPRESTIMO_CONFIRMADO['template'].format(
        nome=emprestimo.usuario.nome,
        titulo=emprestimo.livro.titulo,
        data_emprestimo=data_emprestimo,
        data_devolucao=data_devolucao
    )
    
    if enviar_email(emprestimo.usuario.email, assunto, mensagem):
        registrar_acao(None, emprestimo, 'NOTIFICACAO', descricao=f'Email de confirmação de empréstimo enviado para {emprestimo.usuario.nome}')
        return True
    return False

def enviar_email_lembrete_devolucao_3_dias(emprestimo):
    """
    ⚠️ Lembrete de Devolução (3 dias antes)
    Enviado 3 dias antes do vencimento
    """
    assunto = f"⚠️ Devolução em 3 dias: \"{emprestimo.livro.titulo}\""
    
    # TEMPLATE DE LEMBRETE 3 DIAS - Editável aqui
    data_devolucao = (emprestimo.data_emprestimo + timedelta(days=15)).strftime('%d/%m/%Y')
    
    mensagem = f"""
Olá {emprestimo.usuario.nome},

Seu prazo de devolução está chegando!

📚 Livro: {emprestimo.livro.titulo}
📅 Devolução: {data_devolucao} (em 3 dias)

✅ OPÇÕES:
• Devolver na biblioteca
• Renovar empréstimo (se disponível)
• Solicitar prorrogação

⚠️ Atraso gera multa de R$ 1,00/dia

📱 Gerencie seu empréstimo no sistema!

Equipe da Biblioteca
"""
    
    if enviar_email(emprestimo.usuario.email, assunto, mensagem):
        registrar_acao(None, emprestimo, 'NOTIFICACAO', descricao=f'Email de lembrete 3 dias enviado para {emprestimo.usuario.nome}')
        return True
    return False

def enviar_email_livro_atraso(emprestimo):
    """
    🚨 Livro em Atraso (1 dia após vencimento)
    Enviado quando o livro está em atraso
    """
    assunto = f"🚨 URGENTE: Livro em atraso - \"{emprestimo.livro.titulo}\""
    
    # TEMPLATE DE LIVRO EM ATRASO - Editável aqui
    data_deveria_devolver = (emprestimo.data_emprestimo + timedelta(days=15)).strftime('%d/%m/%Y')
    dias_atraso = (now().date() - (emprestimo.data_emprestimo + timedelta(days=15)).date()).days
    
    mensagem = f"""
Olá {emprestimo.usuario.nome},

Seu livro está em atraso desde ontem.

📚 Livro: {emprestimo.livro.titulo}
📅 Deveria ter sido devolvido: {data_deveria_devolver}
💰 Multa atual: R$ {multa:.2f}

🏃♂️ AÇÃO NECESSÁRIA:
Devolva o livro hoje mesmo na biblioteca.

📍 Horário de funcionamento:
Segunda a Sexta: 8h às 17h

📱 Contato da biblioteca disponível no sistema

Equipe da Biblioteca
"""
    
    if enviar_email(emprestimo.usuario.email, assunto, mensagem):
        registrar_acao(None, emprestimo, 'NOTIFICACAO', descricao=f'Email de livro em atraso enviado para {emprestimo.usuario.nome}')
        return True
    return False

def enviar_email_devolucao_confirmada(emprestimo):
    """
    ✅ Devolução Confirmada
    Enviado quando um livro é devolvido
    """
    assunto = f"✅ Devolução Confirmada: \"{emprestimo.livro.titulo}\""
    
    # TEMPLATE DE DEVOLUÇÃO CONFIRMADA - Editável aqui
    data_devolucao = emprestimo.data_devolucao.strftime('%d/%m/%Y') if emprestimo.data_devolucao else now().strftime('%d/%m/%Y')
    
    mensagem = f"""
Olá {emprestimo.usuario.nome},

Obrigado por devolver o livro! 📚

📖 Livro: {emprestimo.livro.titulo}
📅 Data de Devolução: {data_devolucao}
💰 Multa: R$ 0,00

⭐ Que tal avaliar sua experiência?
Acesse o sistema e deixe sua avaliação!

🔍 Explore mais livros no sistema!

Continue lendo!
Equipe da Biblioteca
"""
    
    if enviar_email(emprestimo.usuario.email, assunto, mensagem):
        registrar_acao(None, emprestimo, 'NOTIFICACAO', descricao=f'Email de devolução confirmada enviado para {emprestimo.usuario.nome}')
        return True
    return False

# -----------------------------------------------------------------------------
# 📋 4. FILA DE ESPERA
# -----------------------------------------------------------------------------

def enviar_email_entrada_fila(reserva):
    """
    🎯 Entrada na Fila
    Enviado quando usuário entra na fila de espera
    📧 TEMPLATE EDITÁVEL EM: email_templates.py -> EMAIL_ENTRADA_FILA
    """
    # CALCULAR POSIÇÃO NA FILA
    posicao = Reserva.objects.filter(
        livro=reserva.livro,
        status='na_fila',
        data_reserva__lt=reserva.data_reserva
    ).count() + 1
    
    total_fila = Reserva.objects.filter(livro=reserva.livro, status='na_fila').count()
    previsao_dias = posicao * PRAZO_EMPRESTIMO_DIAS
    
    # USAR TEMPLATE CONFIGURÁVEL
    assunto = EMAIL_ENTRADA_FILA['assunto'].format(titulo=reserva.livro.titulo)
    mensagem = EMAIL_ENTRADA_FILA['template'].format(
        nome=reserva.aluno.nome,
        titulo=reserva.livro.titulo,
        posicao=posicao,
        total_fila=total_fila,
        previsao_dias=previsao_dias
    )
    
    if enviar_email(reserva.aluno.email, assunto, mensagem):
        registrar_acao(None, reserva, 'NOTIFICACAO', descricao=f'Email de entrada na fila enviado para {reserva.aluno.nome}')
        return True
    return False

def enviar_email_sua_vez_fila(reserva):
    """
    🎉 Sua Vez na Fila
    Enviado quando é a vez do usuário na fila
    📧 TEMPLATE EDITÁVEL EM: email_templates.py -> EMAIL_SUA_VEZ_FILA
    """
    # USAR TEMPLATE CONFIGURÁVEL
    assunto = EMAIL_SUA_VEZ_FILA['assunto'].format(titulo=reserva.livro.titulo)
    mensagem = EMAIL_SUA_VEZ_FILA['template'].format(
        nome=reserva.aluno.nome,
        titulo=reserva.livro.titulo
    )
    
    if enviar_email(reserva.aluno.email, assunto, mensagem):
        registrar_acao(None, reserva, 'NOTIFICACAO', descricao=f'Email de sua vez na fila enviado para {reserva.aluno.nome}')
        return True
    return False

# -----------------------------------------------------------------------------
# 🔔 5. NOTIFICAÇÕES GERAIS
# -----------------------------------------------------------------------------

def enviar_email_novos_livros(usuarios_lista, livros_novos):
    """
    📚 Novos Livros Adicionados
    Enviado quando novos livros são adicionados ao sistema
    """
    assunto = "📚 Novidades na biblioteca! Confira os novos livros"
    
    # TEMPLATE DE NOVOS LIVROS - Editável aqui
    lista_livros = "\n".join([f"• {livro.titulo} - {livro.autor}" for livro in livros_novos[:3]])
    
    for usuario in usuarios_lista:
        mensagem = f"""
Olá {usuario.nome},

Chegaram livros novos na nossa biblioteca! 🎉

📖 DESTAQUES DESTA SEMANA:
{lista_livros}

🔍 Veja todos os novos livros no sistema!

📱 Acesse o sistema da biblioteca!

Boa leitura!
Equipe da Biblioteca
"""
        
        if enviar_email(usuario.email, assunto, mensagem):
            registrar_acao(None, usuario, 'NOTIFICACAO', descricao=f'Email de novos livros enviado para {usuario.nome}')

def enviar_email_recomendacoes(usuario, livros_recomendados):
    """
    ⭐ Recomendações Personalizadas
    Enviado com recomendações baseadas no histórico do usuário
    """
    assunto = f"⭐ Livros especiais para você, {usuario.nome}!"
    
    # TEMPLATE DE RECOMENDAÇÕES - Editável aqui
    lista_recomendados = "\n".join([f"• {livro.titulo} - {livro.autor}" for livro in livros_recomendados[:3]])
    
    mensagem = f"""
Olá {usuario.nome},

Com base no seu histórico, selecionamos estes livros:

📚 RECOMENDADOS PARA VOCÊ:
{lista_recomendados}

🎯 Por que recomendamos:
Você gostou de livros similares no passado!

🔍 Veja as recomendações no sistema!

Equipe da Biblioteca
"""
    
    if enviar_email(usuario.email, assunto, mensagem):
        registrar_acao(None, usuario, 'NOTIFICACAO', descricao=f'Email de recomendações enviado para {usuario.nome}')
        return True
    return False

# -----------------------------------------------------------------------------
# 📊 6. RELATÓRIOS E ESTATÍSTICAS
# -----------------------------------------------------------------------------

def enviar_email_relatorio_mensal(usuario, estatisticas):
    """
    📈 Relatório Mensal do Usuário
    Enviado mensalmente com estatísticas de leitura
    """
    assunto = f"📈 Seu relatório de leitura - {now().strftime('%m/%Y')}"
    
    # TEMPLATE DE RELATÓRIO MENSAL - Editável aqui
    mensagem = f"""
Olá {usuario.nome},

Veja como foi seu mês na biblioteca! 📚

📊 SUAS ESTATÍSTICAS:
• Livros lidos: {estatisticas.get('livros_lidos', 0)}
• Páginas lidas: {estatisticas.get('paginas_lidas', 0)}
• Gênero favorito: {estatisticas.get('genero_favorito', 'Não definido')}
• Tempo médio de leitura: {estatisticas.get('tempo_medio', 0)} dias

🏆 CONQUISTAS:
• Leitor ativo do mês!
• Meta de leitura alcançada!

📚 PRÓXIMAS METAS:
• Ler mais livros este mês
• Explorar novos gêneros

📱 Veja o relatório completo no sistema!

Continue lendo!
Equipe da Biblioteca
"""
    
    if enviar_email(usuario.email, assunto, mensagem):
        registrar_acao(None, usuario, 'NOTIFICACAO', descricao=f'Email de relatório mensal enviado para {usuario.nome}')
        return True
    return False

# -----------------------------------------------------------------------------
# 🚨 7. ALERTAS ADMINISTRATIVOS
# -----------------------------------------------------------------------------

def enviar_email_alerta_admin(admin_email, tipo_alerta, detalhes):
    """
    ⚠️ Alerta de Sistema (Para Admins)
    Enviado para administradores sobre eventos importantes
    """
    assunto = f"🚨 ALERTA: {tipo_alerta} - Sistema Biblioteca"
    
    # TEMPLATE DE ALERTA ADMIN - Editável aqui
    mensagem = f"""
Olá Administrador,

Alerta detectado no sistema:

🔍 DETALHES:
• Tipo: {tipo_alerta}
• Usuário: {detalhes.get('usuario', 'N/A')}
• Livro: {detalhes.get('livro', 'N/A')}
• Data: {now().strftime('%d/%m/%Y %H:%M')}
• Prioridade: {detalhes.get('prioridade', 'Média')}

🔧 AÇÃO NECESSÁRIA:
{detalhes.get('acao', 'Verificar sistema')}

📱 Acesse o painel administrativo!

Sistema de Biblioteca
"""
    
    if enviar_email(admin_email, assunto, mensagem):
        logger.info(f'Email de alerta administrativo enviado: {tipo_alerta}')
        return True
    return False

# -----------------------------------------------------------------------------
# 🎓 8. EMAILS EDUCACIONAIS
# -----------------------------------------------------------------------------

def enviar_email_dicas_leitura(usuarios_lista, dica_titulo, dica_conteudo, livro_sugerido=None):
    """
    💡 Dicas de Leitura
    Enviado semanalmente com dicas educacionais
    """
    assunto = f"💡 Dica da semana: {dica_titulo}"
    
    # TEMPLATE DE DICAS DE LEITURA - Editável aqui
    livro_texto = f"\n\n📚 Livro da semana: \"{livro_sugerido.titulo}\"\nPerfeito para praticar essa técnica!" if livro_sugerido else ""
    
    for usuario in usuarios_lista:
        mensagem = f"""
Olá {usuario.nome},

Dica desta semana para turbinar sua leitura! 📚

💡 DICA: \"{dica_titulo}\"
{dica_conteudo}
{livro_texto}

🔍 Explore mais no sistema!

Boa leitura!
Equipe da Biblioteca
"""
        
        if enviar_email(usuario.email, assunto, mensagem):
            registrar_acao(None, usuario, 'NOTIFICACAO', descricao=f'Email de dicas de leitura enviado para {usuario.nome}')

# -----------------------------------------------------------------------------
# 🎉 9. EVENTOS E PROMOÇÕES
# -----------------------------------------------------------------------------

def enviar_email_convite_evento(usuarios_lista, nome_evento, data_evento, horario, local, programacao):
    """
    🎪 Convite para Eventos
    Enviado para convidar usuários para eventos da biblioteca
    """
    assunto = f"🎪 Convite: {nome_evento} na biblioteca!"
    
    # TEMPLATE DE CONVITE EVENTO - Editável aqui
    programacao_texto = "\n".join([f"• {atividade}" for atividade in programacao])
    
    for usuario in usuarios_lista:
        mensagem = f"""
Olá {usuario.nome},

Você está convidado para nosso evento especial! 🎉

📅 EVENTO: {nome_evento}
📅 Data: {data_evento}
⏰ Horário: {horario}
📍 Local: {local}
👥 Vagas limitadas!

🎯 PROGRAMAÇÃO:
{programacao_texto}

✅ Confirme sua presença no sistema!

📱 Mais informações no sistema!

Te esperamos!
Equipe da Biblioteca
"""
        
        if enviar_email(usuario.email, assunto, mensagem):
            registrar_acao(None, usuario, 'NOTIFICACAO', descricao=f'Email de convite para evento enviado para {usuario.nome}')

# -----------------------------------------------------------------------------
# 📧 FUNÇÃO PARA ENVIO MANUAL DE EMAIL
# -----------------------------------------------------------------------------

def enviar_email_manual(destinatario_email, assunto_personalizado, mensagem_personalizada, remetente_usuario=None):
    """
    📧 Envio Manual de Email
    Permite enviar emails personalizados através do sistema
    """
    if enviar_email(destinatario_email, assunto_personalizado, mensagem_personalizada):
        if remetente_usuario:
            registrar_acao(remetente_usuario, None, 'NOTIFICACAO', 
                         descricao=f'Email manual enviado para {destinatario_email} com assunto: {assunto_personalizado}')
        logger.info(f'Email manual enviado para {destinatario_email}')
        return True
    return False
