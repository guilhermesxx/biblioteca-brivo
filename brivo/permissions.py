from rest_framework.permissions import BasePermission

class EhDonoOuAdmin(BasePermission):
    """
    Permite acesso apenas se o usuário for o dono do empréstimo ou um admin.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj.usuario == request.user
