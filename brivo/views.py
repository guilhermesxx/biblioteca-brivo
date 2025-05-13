from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from .models import Livro, Usuario, Emprestimo
from .serializers import LivroSerializer, UsuarioSerializer, EmprestimoSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer
