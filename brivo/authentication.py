from django.contrib.auth.backends import BaseBackend
from .models import Usuario

class EmailOrUsernameBackend(BaseBackend):
    """
    Backend de autenticação que permite login com email ou username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        user = None
        
        # Tenta por email primeiro
        if '@' in username:
            try:
                user = Usuario.objects.get(email=username)
            except Usuario.DoesNotExist:
                pass
        
        # Se não encontrou por email, tenta por username
        if not user:
            try:
                user = Usuario.objects.get(username=username)
            except Usuario.DoesNotExist:
                pass
        
        # Se ainda não encontrou, tenta por email mesmo sem @
        if not user:
            try:
                user = Usuario.objects.get(email=username)
            except Usuario.DoesNotExist:
                return None
        
        # Verifica a senha
        if user and user.check_password(password) and user.is_active:
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None