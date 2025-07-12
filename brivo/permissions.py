# brivo/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class EhAdmin(BasePermission):
    """
    Permite acesso apenas a usuários do tipo 'admin'.
    """
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado e se o atributo 'tipo' existe e é 'admin'
        return request.user and request.user.is_authenticated and getattr(request.user, 'tipo', None) == "admin"


class EhProfessorOuAdmin(BasePermission):
    """
    Permite acesso a professores e administradores.
    """
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado e se o atributo 'tipo' existe e é 'professor' ou 'admin'
        return request.user and request.user.is_authenticated and getattr(request.user, 'tipo', None) in ["professor", "admin"]


class EhDonoOuAdmin(BasePermission):
    """
    Permite acesso se o usuário for o dono do objeto OU um administrador.
    Esta permissão é flexível para objetos que têm um campo 'usuario' (como Emprestimo, Reserva)
    e para o próprio objeto Usuario (onde o obj é o request.user).
    """
    def has_permission(self, request, view):
        # O usuário deve estar autenticado para qualquer verificação de objeto
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Um administrador sempre tem permissão de objeto
        if getattr(request.user, 'tipo', None) == "admin":
            return True
        
        # Se o objeto é uma instância de Usuario, verifica se é o próprio usuário logado
        if isinstance(obj, request.user.__class__): # Compara o tipo do objeto com o tipo do usuário
            return obj == request.user # Verifica se o objeto é o próprio usuário logado
        
        # Para outros objetos (como Emprestimo, Reserva) que têm um atributo 'usuario'
        # Verifica se o atributo 'usuario' do objeto corresponde ao usuário logado
        return getattr(obj, 'usuario', None) == request.user


class SomenteLeituraOuAdmin(BasePermission):
    """
    Permite leitura (GET, HEAD, OPTIONS) para todos autenticados,
    mas apenas admins podem modificar (POST, PUT, PATCH, DELETE).
    """
    def has_permission(self, request, view):
        # Se o método da requisição é seguro (leitura), permite se o usuário estiver autenticado
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Para métodos de escrita, permite apenas se o usuário for autenticado e do tipo 'admin'
        return request.user and request.user.is_authenticated and getattr(request.user, 'tipo', None) == "admin"
