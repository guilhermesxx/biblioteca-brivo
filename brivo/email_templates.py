# =============================================================================
# 📧 TEMPLATES DE EMAIL CONFIGURÁVEIS
# =============================================================================
# 
# Este arquivo contém todos os templates de email do sistema.
# Você pode editar as mensagens aqui sem mexer no código principal.
# 
# INSTRUÇÕES:
# - Mantenha as variáveis entre {} (ex: {usuario.nome})
# - Não remova as variáveis, apenas edite o texto ao redor
# - Use emojis para deixar os emails mais amigáveis
# - Mantenha o tom profissional mas acolhedor
#
# =============================================================================

# -----------------------------------------------------------------------------
# 🎯 1. AUTENTICAÇÃO E BOAS-VINDAS
# -----------------------------------------------------------------------------

EMAIL_BOAS_VINDAS = {
    'assunto': '🎉 Bem-vindo à Biblioteca Digital da Escola!',
    'template': '''
Olá {nome},

Parabéns! Sua conta foi criada com sucesso na nossa biblioteca digital.

📚 Agora você pode:
• Explorar nosso catálogo completo
• Reservar livros online
• Acompanhar seus empréstimos
• Criar sua lista de favoritos

👤 Seus dados:
• Nome: {nome}
• Email: {email}
• RA: {ra}
• Turma: {turma}
• Tipo: {tipo}

🚀 Comece agora acessando o sistema!

Dúvidas? Responda este email ou procure a biblioteca.

Boa leitura!
Equipe da Biblioteca
'''
}

# -----------------------------------------------------------------------------
# 📚 2. RESERVAS E AGENDAMENTOS
# -----------------------------------------------------------------------------

EMAIL_CONFIRMACAO_RESERVA = {
    'assunto': '📖 Reserva Confirmada: "{titulo}"',
    'template': '''
Olá {nome},

Sua reserva foi confirmada com sucesso! 🎉

📚 Livro: {titulo}
👤 Autor: {autor}
📅 Data de Retirada: {data_retirada}
⏰ Horário: {hora_retirada}
📍 Local: Biblioteca da Escola

⚠️ IMPORTANTE:
• Retire o livro na data agendada
• Leve seu documento de identificação
• Prazo de empréstimo: 15 dias

📱 Acompanhe pelo sistema!

Boa leitura!
Equipe da Biblioteca
'''
}

EMAIL_LEMBRETE_RETIRADA = {
    'assunto': '⏰ Lembrete: Retire seu livro amanhã!',
    'template': '''
Olá {nome},

Não esqueça! Amanhã é o dia de retirar seu livro reservado.

📚 "{titulo}"
📅 Data: {data_retirada} às {hora_retirada}
📍 Local: Biblioteca da Escola

Não consegue comparecer? 
• Reagende pelo sistema
• Ou cancele a reserva

📱 Gerencie sua reserva no sistema!

Até amanhã!
Equipe da Biblioteca
'''
}

EMAIL_RESERVA_CANCELADA = {
    'assunto': '❌ Reserva Cancelada: "{titulo}"',
    'template': '''
Olá {nome},

Sua reserva foi cancelada conforme solicitado.

📚 Livro: {titulo}
📅 Data que seria retirada: {data_seria_retirada}

💡 Quer reservar novamente?
Acesse o sistema e faça uma nova reserva quando desejar.

📱 Explore mais livros no sistema!

Equipe da Biblioteca
'''
}

# -----------------------------------------------------------------------------
# 📖 3. EMPRÉSTIMOS
# -----------------------------------------------------------------------------

EMAIL_EMPRESTIMO_CONFIRMADO = {
    'assunto': '🎉 Empréstimo Realizado: "{titulo}"',
    'template': '''
Olá {nome},

Seu empréstimo foi registrado com sucesso!

📚 Livro: {titulo}
📅 Data do Empréstimo: {data_emprestimo}
📅 Data de Devolução: {data_devolucao}
⏰ Prazo: 15 dias

📋 LEMBRE-SE:
• Cuide bem do livro
• Devolva na data correta
• Prazo de 15 dias para devolução

📱 Acompanhe seu empréstimo no sistema!

Boa leitura!
Equipe da Biblioteca
'''
}

EMAIL_LEMBRETE_DEVOLUCAO_3_DIAS = {
    'assunto': '⚠️ Devolução em 3 dias: "{titulo}"',
    'template': '''
Olá {nome},

Seu prazo de devolução está chegando!

📚 Livro: {titulo}
📅 Devolução: {data_devolucao} (em 3 dias)

✅ OPÇÕES:
• Devolver na biblioteca
• Renovar empréstimo (se disponível)
• Solicitar prorrogação

⚠️ Lembre-se de devolver no prazo

📱 Gerencie seu empréstimo no sistema!

Equipe da Biblioteca
'''
}

EMAIL_LIVRO_ATRASO = {
    'assunto': '🚨 URGENTE: Livro em atraso - "{titulo}"',
    'template': '''
Olá {nome},

Seu livro está em atraso desde ontem.

📚 Livro: {titulo}
📅 Deveria ter sido devolvido: {data_deveria_devolver}
⚠️ Status: Em atraso

🏃‍♂️ AÇÃO NECESSÁRIA:
Devolva o livro hoje mesmo na biblioteca.

📍 Horário de funcionamento:
Segunda a Sexta: 8h às 17h

📱 Contato da biblioteca disponível no sistema

Equipe da Biblioteca
'''
}

EMAIL_DEVOLUCAO_CONFIRMADA = {
    'assunto': '✅ Devolução Confirmada: "{titulo}"',
    'template': '''
Olá {nome},

Obrigado por devolver o livro! 📚

📖 Livro: {titulo}
📅 Data de Devolução: {data_devolucao}
✅ Status: Devolvido com sucesso

⭐ Que tal avaliar sua experiência?
Acesse o sistema e deixe sua avaliação!

🔍 Explore mais livros no sistema!

Continue lendo!
Equipe da Biblioteca
'''
}

# -----------------------------------------------------------------------------
# 📋 4. FILA DE ESPERA
# -----------------------------------------------------------------------------

EMAIL_ENTRADA_FILA = {
    'assunto': '📋 Você entrou na fila: "{titulo}"',
    'template': '''
Olá {nome},

O livro que você quer está emprestado, mas você entrou na fila!

📚 Livro: {titulo}
📊 Sua posição: {posicao} de {total_fila}
⏱️ Previsão: {previsao_dias} dias

📱 Acompanhe a fila no sistema!

Avisaremos quando for sua vez!
Equipe da Biblioteca
'''
}

EMAIL_SUA_VEZ_FILA = {
    'assunto': '🎉 É sua vez! "{titulo}" disponível',
    'template': '''
Olá {nome},

Boa notícia! O livro que você esperava está disponível!

📚 Livro: {titulo}
⏰ Prazo para reservar: 48 horas

🚀 RESERVE AGORA:
Acesse o sistema e agende sua retirada!

⚠️ Se não reservar em 48h, passará para o próximo da fila.

📱 Acesse o sistema agora!

Equipe da Biblioteca
'''
}

# -----------------------------------------------------------------------------
# 🔔 5. NOTIFICAÇÕES GERAIS
# -----------------------------------------------------------------------------

EMAIL_NOVOS_LIVROS = {
    'assunto': '📚 Novidades na biblioteca! Confira os novos livros',
    'template': '''
Olá {nome},

Chegaram livros novos na nossa biblioteca! 🎉

📖 DESTAQUES DESTA SEMANA:
{lista_livros}

🔍 Veja todos os novos livros no sistema!

📱 Acesse o sistema da biblioteca!

Boa leitura!
Equipe da Biblioteca
'''
}

EMAIL_RECOMENDACOES = {
    'assunto': '⭐ Livros especiais para você, {nome}!',
    'template': '''
Olá {nome},

Com base no seu histórico, selecionamos estes livros:

📚 RECOMENDADOS PARA VOCÊ:
{lista_recomendados}

🎯 Por que recomendamos:
Você gostou de livros similares no passado!

🔍 Veja as recomendações no sistema!

Equipe da Biblioteca
'''
}

# -----------------------------------------------------------------------------
# 📊 6. RELATÓRIOS E ESTATÍSTICAS
# -----------------------------------------------------------------------------

EMAIL_RELATORIO_MENSAL = {
    'assunto': '📈 Seu relatório de leitura - {mes_ano}',
    'template': '''
Olá {nome},

Veja como foi seu mês na biblioteca! 📚

📊 SUAS ESTATÍSTICAS:
• Livros lidos: {livros_lidos}
• Páginas lidas: {paginas_lidas}
• Gênero favorito: {genero_favorito}
• Tempo médio de leitura: {tempo_medio} dias

🏆 CONQUISTAS:
• Leitor ativo do mês!
• Meta de leitura alcançada!

📚 PRÓXIMAS METAS:
• Ler mais livros este mês
• Explorar novos gêneros

📱 Veja o relatório completo no sistema!

Continue lendo!
Equipe da Biblioteca
'''
}

# -----------------------------------------------------------------------------
# 🚨 7. ALERTAS ADMINISTRATIVOS
# -----------------------------------------------------------------------------

EMAIL_ALERTA_ADMIN = {
    'assunto': '🚨 ALERTA: {tipo_alerta} - Sistema Biblioteca',
    'template': '''
Olá Administrador,

Alerta detectado no sistema:

🔍 DETALHES:
• Tipo: {tipo_alerta}
• Usuário: {usuario}
• Livro: {livro}
• Data: {data_hora}
• Prioridade: {prioridade}

🔧 AÇÃO NECESSÁRIA:
{acao_necessaria}

📱 Acesse o painel administrativo!

Sistema de Biblioteca
'''
}

# -----------------------------------------------------------------------------
# 🎓 8. EMAILS EDUCACIONAIS
# -----------------------------------------------------------------------------

EMAIL_DICAS_LEITURA = {
    'assunto': '💡 Dica da semana: {dica_titulo}',
    'template': '''
Olá {nome},

Dica desta semana para turbinar sua leitura! 📚

💡 DICA: "{dica_titulo}"
{dica_conteudo}

{livro_sugerido_texto}

🔍 Explore mais no sistema!

Boa leitura!
Equipe da Biblioteca
'''
}

# -----------------------------------------------------------------------------
# 🎉 9. EVENTOS E PROMOÇÕES
# -----------------------------------------------------------------------------

EMAIL_CONVITE_EVENTO = {
    'assunto': '🎪 Convite: {nome_evento} na biblioteca!',
    'template': '''
Olá {nome},

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
'''
}

# =============================================================================
# 📧 CONFIGURAÇÕES GERAIS DE EMAIL
# =============================================================================

# Nome da escola (será substituído automaticamente)
NOME_ESCOLA = "Escola"

# Assinatura padrão
ASSINATURA_PADRAO = "Equipe da Biblioteca"

# Rodapé padrão para todos os emails
RODAPE_PADRAO = """
---
📚 Sistema de Biblioteca Escolar
📧 Este é um email automático, não responda.
📱 Acesse o sistema para mais informações.
"""

# Configurações de horário de funcionamento
HORARIO_FUNCIONAMENTO = "Segunda a Sexta: 8h às 17h"

# Configurações de empréstimo
# MULTA_POR_DIA = 1.00  # Removido - não há multa no sistema escolar

# Prazo padrão de empréstimo em dias
PRAZO_EMPRESTIMO_DIAS = 15