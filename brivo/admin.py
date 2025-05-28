from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Livro, Emprestimo

# Personalização do admin para o modelo Usuario
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('id', 'nome', 'email', 'ra', 'turma', 'tipo', 'is_staff')
    list_filter = ('tipo', 'is_staff', 'turma')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # "password" é o nome correto no AbstractBaseUser
        ('Informações Pessoais', {'fields': ('nome', 'ra', 'turma', 'tipo')}),
        ('Permissões', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'ra', 'nome', 'turma', 'tipo', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'nome', 'ra')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

# Registro do modelo de Livro
class LivroAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'autor', 'tipo', 'disponivel')
    list_filter = ('tipo', 'disponivel', 'data_publicacao')
    search_fields = ('titulo', 'autor', 'editora')
    ordering = ('titulo',)

# Registro do modelo de Empréstimo
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('id', 'livro', 'usuario', 'data_emprestimo', 'devolvido', 'data_devolucao')
    list_filter = ('devolvido', 'data_emprestimo', 'data_devolucao')
    search_fields = ('livro__titulo', 'usuario__nome')
    ordering = ('-data_emprestimo',)

# Registro no admin
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Livro, LivroAdmin)
admin.site.register(Emprestimo, EmprestimoAdmin)
