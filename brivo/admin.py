from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Livro, Emprestimo, AlertaSistema 

# Personalização do admin para o modelo Usuario
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('id', 'nome', 'email', 'ra', 'turma', 'tipo', 'is_staff')
    list_filter = ('tipo', 'is_staff', 'turma')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  
        ('Informações Pessoais', {'fields': ('nome', 'ra', 'turma', 'tipo')}),
        ('Permissões', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'ra', 'nome', 'turma', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'nome', 'ra')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

# Registro do modelo de Livro
class LivroAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'autor', 'tipo', 'quantidade_total', 'quantidade_emprestada', 'quantidade_disponivel', 'disponivel_status')
    
    list_filter = ('tipo', 'genero', 'data_publicacao') 
    search_fields = ('titulo', 'autor', 'editora', 'genero')
    ordering = ('titulo',)

    def disponivel_status(self, obj):
        # Retorna True ou False diretamente para que o Django exiba o ícone booleano
        return obj.disponivel 
    disponivel_status.short_description = 'Disponível'
    disponivel_status.boolean = True # Isso diz ao Django para exibir um ícone booleano

# Registro do modelo de Empréstimo
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('id', 'livro', 'usuario', 'data_emprestimo', 'devolvido', 'data_devolucao')
    list_filter = ('devolvido', 'data_emprestimo', 'data_devolucao')
    search_fields = ('livro__titulo', 'usuario__nome')
    ordering = ('-data_emprestimo',)

# NOVO: Registro do modelo de AlertaSistema
class AlertaSistemaAdmin(admin.ModelAdmin):
    # ATUALIZADO: Inclui os novos campos de visibilidade e agendamento
    list_display = ('id', 'titulo', 'tipo', 'visibilidade', 'data_publicacao', 'expira_em', 'resolvido', 'email_enviado', 'data_criacao')
    # ATUALIZADO: Inclui filtros para os novos campos
    list_filter = ('tipo', 'visibilidade', 'resolvido', 'email_enviado', 'data_publicacao', 'expira_em')
    search_fields = ('titulo', 'mensagem')
    ordering = ('-data_criacao',) 
    list_editable = ('resolvido',) # Permite editar 'resolvido' diretamente na lista


# Registro no admin
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Livro, LivroAdmin)
admin.site.register(Emprestimo, EmprestimoAdmin)
admin.site.register(AlertaSistema, AlertaSistemaAdmin) 
