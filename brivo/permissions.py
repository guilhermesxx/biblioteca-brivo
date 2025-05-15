from rest_framework.permissions import BasePermission, SAFE_METHODS

class EhDonoOuAdmin(BasePermission):
    """
    Permite acesso apenas se o usuário for o dono do objeto ou um admin.
    """

    def has_object_permission(self, request, view, obj):
        # Admin pode acessar tudo
        if request.user.is_admin:
            return True

        # Se for um empréstimo, o dono é quem o criou
        return obj.usuario == request.user
