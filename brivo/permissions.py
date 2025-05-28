from rest_framework.permissions import BasePermission, SAFE_METHODS

class EhAdmin(BasePermission):
    """
    Permite acesso apenas a usuários do tipo 'admin'.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'tipo', None) == "admin"


class EhProfessorOuAdmin(BasePermission):
    """
    Permite acesso a professores e administradores.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'tipo', None) in ["professor", "admin"]


class EhDonoOuAdmin(BasePermission):
    """
    Permite acesso se o usuário for o dono do objeto (empréstimo) ou um administrador.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return getattr(request.user, 'tipo', None) == "admin" or obj.usuario == request.user


class SomenteLeituraOuAdmin(BasePermission):
    """
    Permite leitura (GET, HEAD, OPTIONS) para todos autenticados,
    mas apenas admins podem modificar (POST, PUT, PATCH, DELETE).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and getattr(request.user, 'tipo', None) == "admin"
