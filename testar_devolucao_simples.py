#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from brivo.models import Livro, Usuario, Emprestimo, Reserva
from django.utils import timezone

def testar_devolucao():
    print("=== TESTE DE DEVOLUCAO DE LIVROS ===")
    
    # Buscar um livro para teste
    livro = Livro.objects.filter(ativo=True).first()
    if not livro:
        print("ERRO: Nenhum livro ativo encontrado!")
        return
    
    print(f"Livro de teste: {livro.titulo}")
    print(f"Quantidade total: {livro.quantidade_total}")
    print(f"Quantidade emprestada: {livro.quantidade_emprestada}")
    print(f"Quantidade disponivel: {livro.quantidade_disponivel}")
    print(f"Disponivel: {livro.disponivel}")
    
    # Buscar emprestimos ativos deste livro
    emprestimos_ativos = Emprestimo.objects.filter(livro=livro, devolvido=False)
    print(f"\nEmprestimos ativos: {emprestimos_ativos.count()}")
    
    if emprestimos_ativos.exists():
        emprestimo = emprestimos_ativos.first()
        print(f"Testando devolucao do emprestimo ID: {emprestimo.id}")
        print(f"Usuario: {emprestimo.usuario.nome}")
        
        # Estado antes da devolucao
        print(f"\nANTES DA DEVOLUCAO:")
        print(f"   Livro disponivel: {livro.disponivel}")
        print(f"   Quantidade emprestada: {livro.quantidade_emprestada}")
        print(f"   Quantidade disponivel: {livro.quantidade_disponivel}")
        
        # Marcar como devolvido
        emprestimo.devolvido = True
        emprestimo.data_devolucao = timezone.now()
        emprestimo.save()
        
        # Recarregar o livro para ver as mudancas
        livro.refresh_from_db()
        
        # Estado apos a devolucao
        print(f"\nAPOS A DEVOLUCAO:")
        print(f"   Livro disponivel: {livro.disponivel}")
        print(f"   Quantidade emprestada: {livro.quantidade_emprestada}")
        print(f"   Quantidade disponivel: {livro.quantidade_disponivel}")
        
        if livro.disponivel:
            print("SUCESSO: Livro voltou a ficar disponivel!")
        else:
            print("ERRO: Livro ainda esta indisponivel!")
            
    else:
        print("INFO: Nenhum emprestimo ativo encontrado para teste")
        
        # Criar um emprestimo de teste se possivel
        aluno = Usuario.objects.filter(tipo='aluno', ativo=True).first()
        if aluno and livro.disponivel:
            print(f"\nCriando emprestimo de teste...")
            emprestimo = Emprestimo.objects.create(
                livro=livro,
                usuario=aluno
            )
            print(f"Emprestimo criado: ID {emprestimo.id}")
            
            # Recarregar livro
            livro.refresh_from_db()
            print(f"Apos emprestimo - Disponivel: {livro.disponivel}, Emprestada: {livro.quantidade_emprestada}")
            
            # Agora testar devolucao
            print(f"\nTestando devolucao...")
            emprestimo.devolvido = True
            emprestimo.data_devolucao = timezone.now()
            emprestimo.save()
            
            # Recarregar livro
            livro.refresh_from_db()
            print(f"Apos devolucao - Disponivel: {livro.disponivel}, Emprestada: {livro.quantidade_emprestada}")
            
            if livro.disponivel:
                print("SUCESSO: Sistema funcionando corretamente!")
            else:
                print("ERRO: Bug ainda existe!")

if __name__ == '__main__':
    testar_devolucao()