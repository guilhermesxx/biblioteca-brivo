from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from .models import Livro, Usuario, Emprestimo
from .serializers import LivroSerializer, UsuarioSerializer, EmprestimoSerializer
from .permissions import EhDonoOuAdmin

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

class EmprestimoListView(generics.ListCreateAPIView):
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.tipo == "professor":
            return Emprestimo.objects.all()
        return Emprestimo.objects.filter(usuario=user)

class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated, EhDonoOuAdmin]

    def perform_create(self, serializer):
        emprestimo = serializer.save()
        emprestimo.livro.disponivel = False
        emprestimo.livro.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        devolvido_antes = instance.devolvido
        emprestimo = serializer.save()

        # Se acabou de ser devolvido
        if not devolvido_antes and emprestimo.devolvido:
            emprestimo.marcar_devolucao()

class EmprestimoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated, EhDonoOuAdmin]
