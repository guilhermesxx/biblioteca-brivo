import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

print("=" * 50)
print("ANÁLISE DE CONFIGURAÇÃO DO BANCO DE DADOS")
print("=" * 50)

# Verifica DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
print(f"DATABASE_URL no ambiente: {'SIM' if database_url else 'NÃO'}")

if database_url:
    print(f"URL: {database_url}")
    if 'postgresql' in database_url:
        print("🐘 BANCO: PostgreSQL (Online)")
    elif 'sqlite' in database_url:
        print("📁 BANCO: SQLite")
    else:
        print("❓ BANCO: Outro tipo")
else:
    print("📁 BANCO: SQLite local (padrão)")

print("\nArquivos de banco encontrados:")
if os.path.exists('db.sqlite3'):
    size = os.path.getsize('db.sqlite3')
    print(f"✅ db.sqlite3 existe ({size} bytes)")
else:
    print("❌ db.sqlite3 não encontrado")

print("=" * 50)