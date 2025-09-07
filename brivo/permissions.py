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
    Esta permissão é flexível para objetos que têm um campo 'usuario' (como Emprestimo)
    ou um campo 'aluno' (como Reserva), e para o próprio objeto Usuario.
    """
    def has_permission(self, request, view):
        # O usuário deve estar autenticado para qualquer verificação de objeto
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Um administrador sempre tem permissão de objeto
        if getattr(request.user, 'tipo', None) == "admin":
            return True
        
        # Se o objeto é uma instância de Usuario, verifica se é o próprio usuário logado
        if isinstance(obj, request.user.__class__):
            return obj == request.user
        
        # Tenta verificar se o usuário é o dono através do campo 'usuario' (para Emprestimo)
        if hasattr(obj, 'usuario') and obj.usuario == request.user:
            return True
            
        # Tenta verificar se o usuário é o dono através do campo 'aluno' (para Reserva)
        if hasattr(obj, 'aluno') and obj.aluno == request.user:
            return True
            
        return False # Nenhuma das condições acima foi atendida


class ApenasAdminPodeEditar(BasePermission):
    """
    Permite leitura para usuários autenticados, mas apenas admins podem editar.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Para métodos de leitura, permite qualquer usuário autenticado
        if request.method in SAFE_METHODS:
            return True
        
        # Para métodos de escrita, apenas admins
        return getattr(request.user, 'tipo', None) == "admin"
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Para métodos de leitura, permite qualquer usuário autenticado
        if request.method in SAFE_METHODS:
            return True
        
        # Para métodos de escrita, apenas admins
        return getattr(request.user, 'tipo', None) == "admin"


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
