#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from brivo.models import Livro, Usuario, Emprestimo, Reserva
from django.utils import timezone

def testar_devolucao():
    print("=== TESTE DE DEVOLUÇÃO DE LIVROS ===")
    
    # Buscar um livro para teste
    livro = Livro.objects.filter(ativo=True).first()
    if not livro:
        print("❌ Nenhum livro ativo encontrado!")
        return
    
    print(f"📚 Livro de teste: {livro.titulo}")
    print(f"📊 Quantidade total: {livro.quantidade_total}")
    print(f"📊 Quantidade emprestada: {livro.quantidade_emprestada}")
    print(f"📊 Quantidade disponível: {livro.quantidade_disponivel}")
    print(f"✅ Disponível: {livro.disponivel}")
    
    # Buscar empréstimos ativos deste livro
    emprestimos_ativos = Emprestimo.objects.filter(livro=livro, devolvido=False)
    print(f"\n📋 Empréstimos ativos: {emprestimos_ativos.count()}")
    
    if emprestimos_ativos.exists():
        emprestimo = emprestimos_ativos.first()
        print(f"🔄 Testando devolução do empréstimo ID: {emprestimo.id}")
        print(f"👤 Usuário: {emprestimo.usuario.nome}")
        
        # Estado antes da devolução
        print(f"\n📊 ANTES DA DEVOLUÇÃO:")
        print(f"   Livro disponível: {livro.disponivel}")
        print(f"   Quantidade emprestada: {livro.quantidade_emprestada}")
        print(f"   Quantidade disponível: {livro.quantidade_disponivel}")
        
        # Marcar como devolvido
        emprestimo.devolvido = True
        emprestimo.data_devolucao = timezone.now()
        emprestimo.save()
        
        # Recarregar o livro para ver as mudanças
        livro.refresh_from_db()
        
        # Estado após a devolução
        print(f"\n📊 APÓS A DEVOLUÇÃO:")
        print(f"   Livro disponível: {livro.disponivel}")
        print(f"   Quantidade emprestada: {livro.quantidade_emprestada}")
        print(f"   Quantidade disponível: {livro.quantidade_disponivel}")
        
        if livro.disponivel:
            print("✅ SUCESSO: Livro voltou a ficar disponível!")
        else:
            print("❌ ERRO: Livro ainda está indisponível!")
            
    else:
        print("ℹ️ Nenhum empréstimo ativo encontrado para teste")
        
        # Criar um empréstimo de teste se possível
        aluno = Usuario.objects.filter(tipo='aluno', ativo=True).first()
        if aluno and livro.disponivel:
            print(f"\n🔄 Criando empréstimo de teste...")
            emprestimo = Emprestimo.objects.create(
                livro=livro,
                usuario=aluno
            )
            print(f"✅ Empréstimo criado: ID {emprestimo.id}")
            
            # Recarregar livro
            livro.refresh_from_db()
            print(f"📊 Após empréstimo - Disponível: {livro.disponivel}, Emprestada: {livro.quantidade_emprestada}")
            
            # Agora testar devolução
            print(f"\n🔄 Testando devolução...")
            emprestimo.devolvido = True
            emprestimo.data_devolucao = timezone.now()
            emprestimo.save()
            
            # Recarregar livro
            livro.refresh_from_db()
            print(f"📊 Após devolução - Disponível: {livro.disponivel}, Emprestada: {livro.quantidade_emprestada}")
            
            if livro.disponivel:
                print("✅ SUCESSO: Sistema funcionando corretamente!")
            else:
                print("❌ ERRO: Bug ainda existe!")

if __name__ == '__main__':
    testar_devolucao()