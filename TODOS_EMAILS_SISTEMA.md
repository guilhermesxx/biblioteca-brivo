# 📧 TODOS OS EMAILS DO SISTEMA BRIVO

## 🎯 1. BOAS-VINDAS (Automático)
**Assunto:** 🎉 Bem-vindo à Biblioteca Digital da Escola!
**Quando:** Ao criar conta nova
```
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
```

## 📚 2. RESERVA CONFIRMADA (Automático)
**Assunto:** 📖 Reserva Confirmada: "{titulo}"
**Quando:** Ao fazer reserva com data/hora
```
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
```

## 📋 3. ENTRADA NA FILA (Automático)
**Assunto:** 📋 Você entrou na fila: "{titulo}"
**Quando:** Ao reservar livro indisponível
```
Olá {nome},

O livro que você quer está emprestado, mas você entrou na fila!

📚 Livro: {titulo}
📊 Sua posição: {posicao} de {total_fila}
⏱️ Previsão: {previsao_dias} dias

📱 Acompanhe a fila no sistema!

Avisaremos quando for sua vez!
Equipe da Biblioteca
```

## 🎉 4. SUA VEZ NA FILA (Automático)
**Assunto:** 🎉 É sua vez! "{titulo}" disponível
**Quando:** Livro da fila fica disponível
```
Olá {nome},

Boa notícia! O livro que você esperava está disponível!

📚 Livro: {titulo}
⏰ Prazo para reservar: 48 horas

🚀 RESERVE AGORA:
Acesse o sistema e agende sua retirada!

⚠️ Se não reservar em 48h, passará para o próximo da fila.

📱 Acesse o sistema agora!

Equipe da Biblioteca
```

## 🎉 5. EMPRÉSTIMO CONFIRMADO (Automático)
**Assunto:** 🎉 Empréstimo Realizado: "{titulo}"
**Quando:** Ao pegar livro emprestado
```
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
```

## ✅ 6. DEVOLUÇÃO CONFIRMADA (Automático)
**Assunto:** ✅ Devolução Confirmada: "{titulo}"
**Quando:** Ao devolver livro
```
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
```

## ⚠️ 7. LEMBRETE DEVOLUÇÃO 3 DIAS (Manual)
**Assunto:** ⚠️ Devolução em 3 dias: "{titulo}"
**Quando:** 3 dias antes do vencimento
```
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
```

## 🚨 8. LIVRO EM ATRASO (Manual)
**Assunto:** 🚨 URGENTE: Livro em atraso - "{titulo}"
**Quando:** Livro em atraso
```
Olá {nome},

Seu livro está em atraso desde ontem.

📚 Livro: {titulo}
📅 Deveria ter sido devolvido: {data_deveria_devolver}
⚠️ Status: Em atraso

🏃♂️ AÇÃO NECESSÁRIA:
Devolva o livro hoje mesmo na biblioteca.

📍 Horário de funcionamento:
Segunda a Sexta: 8h às 17h

📱 Contato da biblioteca disponível no sistema

Equipe da Biblioteca
```

## ⏰ 9. LEMBRETE RETIRADA (Manual)
**Assunto:** ⏰ Lembrete: Retire seu livro amanhã!
**Quando:** 1 dia antes da retirada
```
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
```

## ❌ 10. RESERVA CANCELADA (Manual)
**Assunto:** ❌ Reserva Cancelada: "{titulo}"
**Quando:** Reserva é cancelada
```
Olá {nome},

Sua reserva foi cancelada conforme solicitado.

📚 Livro: {titulo}
📅 Data que seria retirada: {data_seria_retirada}

💡 Quer reservar novamente?
Acesse o sistema e faça uma nova reserva quando desejar.

📱 Explore mais livros no sistema!

Equipe da Biblioteca
```

## 📚 11. NOVOS LIVROS (Manual)
**Assunto:** 📚 Novidades na biblioteca! Confira os novos livros
**Quando:** Administrador envia manualmente
```
Olá {nome},

Chegaram livros novos na nossa biblioteca! 🎉

📖 DESTAQUES DESTA SEMANA:
{lista_livros}

🔍 Veja todos os novos livros no sistema!

📱 Acesse o sistema da biblioteca!

Boa leitura!
Equipe da Biblioteca
```

## ⭐ 12. RECOMENDAÇÕES (Manual)
**Assunto:** ⭐ Livros especiais para você, {nome}!
**Quando:** Administrador envia manualmente
```
Olá {nome},

Com base no seu histórico, selecionamos estes livros:

📚 RECOMENDADOS PARA VOCÊ:
{lista_recomendados}

🎯 Por que recomendamos:
Você gostou de livros similares no passado!

🔍 Veja as recomendações no sistema!

Equipe da Biblioteca
```

## 📈 13. RELATÓRIO MENSAL (Manual)
**Assunto:** 📈 Seu relatório de leitura - {mes_ano}
**Quando:** Administrador envia mensalmente
```
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
```

## 💡 14. DICAS DE LEITURA (Manual)
**Assunto:** 💡 Dica da semana: {dica_titulo}
**Quando:** Administrador envia semanalmente
```
Olá {nome},

Dica desta semana para turbinar sua leitura! 📚

💡 DICA: "{dica_titulo}"
{dica_conteudo}

{livro_sugerido_texto}

🔍 Explore mais no sistema!

Boa leitura!
Equipe da Biblioteca
```

## 🎪 15. CONVITE EVENTO (Manual)
**Assunto:** 🎪 Convite: {nome_evento} na biblioteca!
**Quando:** Administrador envia para eventos
```
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
```

## 🚨 16. ALERTA ADMIN (Automático)
**Assunto:** 🚨 ALERTA: {tipo_alerta} - Sistema Biblioteca
**Quando:** Alertas do sistema para admins
```
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
```

## 🔔 17. ALERTA PÚBLICO (Automático)
**Assunto:** Alerta da Biblioteca: {titulo}
**Quando:** Alertas públicos do sistema
```
Ola!

A Biblioteca Escolar tem um novo alerta para voce:

Titulo: {titulo}
Mensagem: {mensagem}

Tipo de Alerta: {tipo_display}
Data de Publicacao: {data_publicacao}
Expira em: {expira_em}

Por favor, verifique o sistema para mais detalhes.

Atenciosamente,
Sistema de Biblioteca Escolar
```

---

## 📊 RESUMO DOS EMAILS:

**✅ AUTOMÁTICOS (7):**
1. Boas-vindas
2. Reserva confirmada  
3. Entrada na fila
4. Sua vez na fila
5. Empréstimo confirmado
6. Devolução confirmada
7. Alertas públicos

**📝 MANUAIS (10):**
8. Lembrete devolução 3 dias
9. Livro em atraso
10. Lembrete retirada
11. Reserva cancelada
12. Novos livros
13. Recomendações
14. Relatório mensal
15. Dicas de leitura
16. Convite evento
17. Alerta admin

**TOTAL: 17 tipos de emails diferentes! 📧**