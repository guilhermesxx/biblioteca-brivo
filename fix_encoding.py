import json

input_filename = "sqlite_data.json"
output_filename = "sqlite_data_fixed.json"

try:
    print(f"Tentando ler o arquivo '{input_filename}' com codificação cp1252...")
    with open(input_filename, "r", encoding="cp1252") as infile:
        data = json.load(infile)

    print(f"Salvando o conteúdo corrigido em '{output_filename}' com codificação utf-8...")
    with open(output_filename, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2)

    print("\nSUCESSO! O arquivo foi corrigido. Agora use o novo arquivo para carregar os dados.")
    print(f"Próximo passo: python manage.py loaddata {output_filename}")

except UnicodeDecodeError:
    print("Erro: Não foi possível decodificar o arquivo com a codificação cp1252.")
    print("Por favor, tente abrir 'sqlite_data.json' no VS Code e salve-o com a codificação 'UTF-8'.")
except FileNotFoundError:
    print(f"Erro: O arquivo '{input_filename}' não foi encontrado.")
except json.JSONDecodeError as e:
    print(f"Erro: O arquivo '{input_filename}' não é um JSON válido. Verifique se ele está completo.")
    print(f"Detalhes do erro: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
