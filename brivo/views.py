from django.shortcuts import render
from rest_framework import viewsets
from .models import Livro, Usuario, Emprestimo
from .serializers import LivroSerializer, UsuarioSerializer, EmprestimoSerializer
from rest_framework import generics
from .models import Emprestimo
from .serializers import EmprestimoSerializer
from .permissions import EhDonoOuAdmin
from rest_framework.permissions import IsAuthenticated

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
class EmprestimoListView(generics.ListCreateAPIView):
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.tipo == "professor":
            return Emprestimo.objects.all()
        return Emprestimo.objects.filter(usuario=user)

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer

    def perform_create(self, serializer):
        emprestimo = serializer.save()
        # Quando criar um empréstimo, marca o livro como indisponível
        livro = emprestimo.livro
        livro.disponivel = False
        livro.save()

    def perform_update(self, serializer):
        emprestimo = serializer.save()
        # Se devolvido = True, torna o livro disponível novamente
        if emprestimo.devolvido:
            livro = emprestimo.livro
            livro.disponivel = True
            livro.save()


class EmprestimoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer
    permission_classes = [EhDonoOuAdmin]
