# 🏗️ Brivo Backend - API de Biblioteca Digital

<div align="center">

![Brivo Backend Logo](https://img.shields.io/badge/Brivo-Backend-2563EB?style=for-the-badge&logo=django&logoColor=white)

**API REST robusta e escalável para gerenciamento completo de bibliotecas escolares**

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)](https://jwt.io/)

[🚀 Instalação](#-instalação) • [📡 API](#-endpoints-da-api) • [🏗️ Arquitetura](#️-arquitetura) • [📊 Dashboard](#-dashboard-e-relatórios) • [📧 Emails](#-sistema-de-emails)

</div>

---

## 🌟 Visão Geral

O **Brivo Backend** é uma API REST completa desenvolvida em Django, projetada para oferecer todas as funcionalidades necessárias para o gerenciamento moderno de bibliotecas escolares. Com arquitetura robusta, sistema de permissões granular e funcionalidades avançadas como controle automático de estoque e sistema de emails inteligente.

### 🎯 Principais Diferenciais

- 🏗️ **Arquitetura Django**: Seguindo as melhores práticas do framework
- 🔐 **Autenticação JWT**: Sistema seguro com tipos de usuário
- 📊 **Dashboard Inteligente**: Estatísticas e métricas em tempo real
- 🤖 **Automação Avançada**: Alertas e notificações automáticas
- 📧 **Sistema de Emails**: Completo com templates e agendamento
- 🔄 **API RESTful**: Endpoints bem estruturados e documentados

---

## 🏗️ Arquitetura

<div align="center">

### 🎯 Modelos de Dados
*Sistema relacional completo com validações inteligentes*

### 🔐 Sistema de Permissões
*Controle granular baseado em tipos de usuário*

### 📡 API REST
*Endpoints organizados com filtros e paginação*

### 🤖 Automação
*Alertas automáticos e controle de estoque inteligente*

</div>

---

## ✨ Funcionalidades

### 👑 Sistema de Usuários
- 🔐 **Autenticação JWT**: Login seguro com validação de tipo
- 👥 **Tipos de Usuário**: Aluno, Professor, Administrador
- 🛡️ **Permissões Granulares**: Controle de acesso por endpoint
- 📊 **Perfis Completos**: RA, turma, estatísticas pessoais
- 🔄 **Soft Delete**: Desativação sem perda de dados

### 📚 Gestão de Acervo
- 📖 **CRUD Completo**: Criação, leitura, atualização e exclusão
- 🏷️ **Categorização**: Gêneros e subgêneros organizados
- 📊 **Controle de Estoque**: Quantidade total e emprestada
- 🔍 **Busca Avançada**: Filtros por título, autor, gênero
- 🤖 **Alertas Automáticos**: Estoque baixo e livros esgotados

### 📅 Sistema de Reservas Inteligente
- 🎯 **Múltiplos Status**: Na fila, aguardando retirada, emprestado
- ⏰ **Agendamento**: Data e hora específicas para retirada
- 🔔 **Notificações**: Automáticas para próximo da fila
- ✅ **Validações**: Conflitos de horário e disponibilidade
- 📧 **Emails Automáticos**: Confirmações e lembretes

### 💼 Empréstimos e Devoluções
- 📋 **Gestão Completa**: Controle total do ciclo de empréstimo
- 🔄 **Atualização Automática**: Estoque atualizado em tempo real
- 📅 **Controle de Prazos**: Datas de devolução e vencimentos
- 🔔 **Lembretes**: Notificações de devolução próxima
- 📊 **Histórico**: Rastreamento completo de atividades

### 🚨 Sistema de Alertas Avançado
- 🤖 **Automáticos**: Estoque baixo, livros esgotados
- 📝 **Manuais**: Criação de alertas personalizados
- ⏰ **Agendamento**: Publicação futura de notificações
- 👥 **Visibilidade**: Admin-only ou público
- 📧 **Integração Email**: Notificações automáticas

---

## 📊 Dashboard e Relatórios

### 📈 Dashboard Administrativo
```python
# Estatísticas em tempo real
{
  "livros": {
    "total": 1247,
    "ativos": 1180,
    "inativos": 67
  },
  "emprestimos": {
    "ativos": 89,
    "devolvidos": 2341
  },
  "usuarios": {
    "alunos": 450,
    "professores": 25,
    "admins": 3
  }
}
```

### 📊 Relatórios Pedagógicos
- 🎓 **Alunos Mais Ativos**: Top 10 por empréstimos
- 📚 **Livros Populares**: Mais emprestados e reservados
- 📈 **Gráficos Temporais**: Empréstimos e reservas por mês
- 🎯 **Insights Automáticos**: Análises de comportamento
- 📋 **Exportação**: Dados para relatórios externos

---

## 📧 Sistema de Emails

### 🤖 Emails Automáticos
- 👋 **Boas-vindas**: Novos usuários cadastrados
- ✅ **Confirmações**: Reservas e empréstimos realizados
- 🔔 **Lembretes**: Devoluções próximas do vencimento
- 📢 **Notificações**: Alertas públicos do sistema
- 🎯 **Disponibilidade**: Livro disponível para reserva

### 📝 Emails Manuais
```python
# Envio individual
POST /api/emails/enviar-manual/
{
  "destinatario": "aluno@escola.com",
  "assunto": "Novo livro disponível",
  "mensagem": "Confira nossa nova aquisição!"
}

# Envio em grupo
POST /api/emails/enviar-grupo/
{
  "tipo_usuarios": ["aluno", "professor"],
  "assunto": "Evento da biblioteca",
  "mensagem": "Participe da nossa feira literária!"
}
```

### 📋 Templates Predefinidos
- 📚 **Novos Livros**: Notificação de aquisições
- 💡 **Dicas de Leitura**: Conteúdo educacional semanal
- 🎉 **Eventos**: Convites para atividades da biblioteca
- 📊 **Relatórios**: Resumos mensais personalizados

---

## 🚀 Instalação

### 📋 Pré-requisitos

```bash
# Python 3.9+ e pip
python --version  # v3.9.0+
pip --version     # 21.0.0+

# PostgreSQL (opcional, usa SQLite por padrão)
psql --version    # 13.0+
```

### ⚡ Início Rápido

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/biblioteca-brivo.git
cd biblioteca-brivo

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 5. Execute as migrações
python manage.py migrate

# 6. Crie um superusuário
python manage.py createsuperuser

# 7. Inicie o servidor
python manage.py runserver
```

### 🐳 Docker (Opcional)

```bash
# Build da imagem
docker build -t brivo-backend .

# Executar container
docker run -p 8000:8000 brivo-backend

# Com docker-compose
docker-compose up -d
```

---

## 🛠️ Tecnologias

### 🏗️ Core
- **Django 5.2.4** - Framework web robusto
- **Django REST Framework 3.16.0** - API REST poderosa
- **Simple JWT 5.5.1** - Autenticação JWT
- **Django Filter 25.1** - Filtros avançados

### 🗄️ Banco de Dados
- **PostgreSQL** - Banco principal (produção)
- **SQLite** - Desenvolvimento local
- **psycopg2** - Driver PostgreSQL
- **dj-database-url** - Configuração flexível

### 📧 Comunicação
- **Django Email** - Sistema de emails nativo
- **Templates HTML** - Emails responsivos
- **SMTP Gmail** - Servidor de email configurado
- **Agendamento** - Envios programados

### 🔧 Utilitários
- **python-dotenv** - Variáveis de ambiente
- **Pillow** - Processamento de imagens
- **django-cors-headers** - CORS para frontend
- **Gunicorn** - Servidor WSGI para produção

---

## 📁 Estrutura do Projeto

```
biblioteca-brivo/
├── 🏗️ biblioteca/              # Configurações Django
│   ├── settings.py             # Configurações principais
│   ├── urls.py                 # URLs raiz
│   └── wsgi.py                 # WSGI para produção
├── 📚 brivo/                   # App principal
│   ├── models.py               # Modelos de dados
│   ├── views.py                # Views da API
│   ├── serializers.py          # Serializers DRF
│   ├── urls.py                 # Rotas da API
│   ├── permissions.py          # Permissões customizadas
│   ├── utils.py                # Utilitários e emails
│   ├── constants.py            # Constantes do sistema
│   └── migrations/             # Migrações do banco
├── 🧪 teste_biblioteca/        # Interface de teste
│   ├── index.html              # Dashboard web
│   ├── script.js               # Lógica frontend
│   └── styles.css              # Estilos CSS
├── 📊 qr-system/               # Sistema QR Code
│   ├── qr-generator.js         # Gerador de QR
│   └── server.js               # Servidor QR
└── 📋 requirements.txt         # Dependências Python
```

---

## 📡 Endpoints da API

### 🔐 Autenticação
```http
POST /api/token/                # Login JWT
POST /api/token/refresh/        # Refresh token
GET  /api/usuarios/me/          # Dados do usuário logado
```

### 👥 Usuários
```http
GET    /api/usuarios/           # Listar usuários
POST   /api/usuarios/           # Criar usuário
GET    /api/usuarios/{id}/      # Detalhes do usuário
PUT    /api/usuarios/{id}/      # Atualizar usuário
DELETE /api/usuarios/{id}/      # Deletar usuário
```

### 📚 Livros
```http
GET    /api/livros/             # Listar livros
POST   /api/livros/             # Criar livro
GET    /api/livros/{id}/        # Detalhes do livro
PUT    /api/livros/{id}/        # Atualizar livro
DELETE /api/livros/{id}/        # Deletar livro
```

### 📅 Reservas
```http
GET    /api/reservas/           # Listar reservas
POST   /api/reservas/           # Criar reserva
PUT    /api/reservas/{id}/      # Atualizar reserva
DELETE /api/reservas/{id}/      # Cancelar reserva
POST   /api/reservas/{id}/efetivar-emprestimo/  # Efetivar empréstimo
```

### 💼 Empréstimos
```http
GET    /api/emprestimos/        # Listar empréstimos
POST   /api/emprestimos/        # Criar empréstimo
PUT    /api/emprestimos/{id}/   # Atualizar empréstimo
GET    /api/emprestimos/recent-reads/  # Últimas leituras
```

### 🚨 Alertas do Sistema
```http
GET    /api/alertas-sistema/    # Listar alertas (admin)
POST   /api/alertas-sistema/    # Criar alerta
PUT    /api/alertas-sistema/{id}/  # Atualizar alerta
DELETE /api/alertas-sistema/{id}/  # Deletar alerta
GET    /api/alertas/publicos/   # Alertas públicos
```

### 📊 Dashboard e Relatórios
```http
GET    /api/dashboard/          # Dashboard admin
GET    /api/relatorios/pedagogicos/  # Relatórios pedagógicos
```

### 📧 Sistema de Emails
```http
POST   /api/emails/enviar-manual/     # Email individual
POST   /api/emails/enviar-grupo/      # Email em grupo
POST   /api/emails/predefinidos/      # Templates predefinidos
GET    /api/emails/tipos/             # Tipos disponíveis
```

---

## 🔧 Configuração

### 🌐 Variáveis de Ambiente

```env
# Django Settings
DJANGO_SECRET_KEY=sua-chave-secreta-super-segura
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/biblioteca_db

# Email Configuration
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=Biblioteca Escolar <biblioteca@escola.com>

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60  # minutos
JWT_REFRESH_TOKEN_LIFETIME=365  # dias
```

### ⚙️ Configuração do Banco

```python
# settings.py - Configuração automática
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # PostgreSQL (Produção)
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, ssl_require=True)
    }
else:
    # SQLite (Desenvolvimento)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

---

## 🔐 Sistema de Permissões

### 🛡️ Permissões Customizadas

```python
# permissions.py
class EhAdmin(BasePermission):
    """Apenas administradores podem acessar"""
    def has_permission(self, request, view):
        return request.user.tipo == 'admin'

class EhDonoOuAdmin(BasePermission):
    """Usuário dono do recurso ou admin"""
    def has_object_permission(self, request, view, obj):
        return obj.usuario == request.user or request.user.tipo == 'admin'

class EhProfessorOuAdmin(BasePermission):
    """Professores e administradores"""
    def has_permission(self, request, view):
        return request.user.tipo in ['professor', 'admin']
```

### 🎯 Aplicação por Endpoint

```python
# views.py - Exemplo de uso
class LivroViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]  # Qualquer usuário logado
        return [IsAuthenticated(), EhAdmin()]  # Apenas admin para modificações
```

---

## 🤖 Automação e Alertas

### 🔔 Alertas Automáticos

```python
# models.py - Sistema inteligente de alertas
def _check_and_create_low_stock_alert(self):
    """Cria alertas automáticos para estoque baixo"""
    if self.quantidade_disponivel <= ESTOQUE_BAIXO_LIMITE:
        AlertaSistema.objects.create(
            titulo=f"Livro: {self.titulo} - Estoque Baixo",
            mensagem=f"Apenas {self.quantidade_disponivel} exemplares disponíveis",
            tipo='warning',
            visibilidade='admin_only'
        )
```

### 📧 Emails Automáticos

```python
# utils.py - Sistema de notificações
def enviar_email_confirmacao_reserva(reserva):
    """Envia email automático de confirmação"""
    template = get_template('emails/confirmacao_reserva.html')
    context = {
        'usuario': reserva.aluno,
        'livro': reserva.livro,
        'data_retirada': reserva.data_retirada_prevista
    }
    
    send_mail(
        subject=f'Reserva Confirmada: {reserva.livro.titulo}',
        message='',
        html_message=template.render(context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reserva.aluno.email]
    )
```

---

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Testes com coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Testes específicos
python manage.py test brivo.tests.test_models
python manage.py test brivo.tests.test_views
python manage.py test brivo.tests.test_api
```

### 📋 Estrutura de Testes

```python
# tests.py - Exemplo de teste
class LivroModelTest(TestCase):
    def test_controle_estoque_automatico(self):
        """Testa se o controle de estoque funciona corretamente"""
        livro = Livro.objects.create(
            titulo="Teste",
            autor="Autor Teste",
            quantidade_total=5
        )
        
        # Criar empréstimo
        emprestimo = Emprestimo.objects.create(
            livro=livro,
            usuario=self.usuario_teste
        )
        
        # Verificar se estoque foi atualizado
        livro.refresh_from_db()
        self.assertEqual(livro.quantidade_emprestada, 1)
        self.assertEqual(livro.quantidade_disponivel, 4)
```

---

## 📦 Deploy

### 🚀 Deploy no Render

```bash
# 1. Configure as variáveis de ambiente no Render
DATABASE_URL=postgresql://...
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=False

# 2. Build automático via GitHub
# O Render detecta automaticamente requirements.txt

# 3. Comando de build
pip install -r requirements.txt

# 4. Comando de start
gunicorn biblioteca.wsgi:application
```

### 🐳 Deploy com Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "biblioteca.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### ☁️ Deploy na AWS/Heroku

```bash
# Heroku
heroku create brivo-backend
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set DJANGO_SECRET_KEY=sua-chave
git push heroku main

# AWS Elastic Beanstalk
eb init brivo-backend
eb create production
eb deploy
```

---

## 🔍 Monitoramento

### 📊 Logs e Debugging

```python
# settings.py - Configuração de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'django_debug.log',
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'brivo': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 📈 Métricas de Performance

```python
# utils.py - Monitoramento de performance
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"{func.__name__} executado em {end_time - start_time:.2f}s")
        return result
    return wrapper
```

---

## 🤝 Contribuição

Contribuições são sempre bem-vindas! Veja como você pode ajudar:

1. 🍴 **Fork** o projeto
2. 🌿 **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. 📝 **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. 📤 **Push** para a branch (`git push origin feature/AmazingFeature`)
5. 🔄 **Abra** um Pull Request

### 📋 Guidelines de Desenvolvimento

- ✅ Siga as convenções do Django e PEP 8
- 🧪 Adicione testes para novas funcionalidades
- 📚 Documente APIs com docstrings detalhadas
- 🔐 Implemente validações de segurança adequadas
- 📊 Adicione logs para operações importantes

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Equipe

<div align="center">

**Desenvolvido com ❤️ para potencializar a gestão de bibliotecas escolares**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/seu-usuario)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/seu-perfil)

</div>

---

## 📞 Suporte

Encontrou um bug ou tem uma sugestão? 

- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/biblioteca-brivo/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/biblioteca-brivo/discussions)
- 📧 **Email**: dev@brivo.com
- 📖 **Documentação**: [Wiki do Projeto](https://github.com/seu-usuario/biblioteca-brivo/wiki)

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

![Brivo Backend](https://img.shields.io/badge/Made_with-❤️-red?style=for-the-badge)

</div>