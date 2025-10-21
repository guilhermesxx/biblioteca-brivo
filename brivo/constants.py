# Gêneros e subgêneros para validação e API
GENEROS_SUBGENEROS = {
    'Catálogo da biblioteca': [],
    'Autores clássicos': [],
    'Gramática': [],
    'Literatura': ['indígena', 'afro', 'cordel'],
    'Pedagógico': [],
    'Arte': [],
    'Música': [],
    'Teatro': [],
    'Cinema': [],
    'Religião': [],
    'Geografia': [],
    'História': [],
    'Ciências': [],
    'Filosofia': [],
    'Meio ambiente': [],
    'Física': [],
    'Educação física': [],
    'Química': [],
    'Matemática': [],
    'Sociologia': [],
    'Infanto juvenil': [],
    'Dicionário': [],
    'Administração': [],
    'Tecnologia': [],
    'Bibliografia': [],
    'Coletânea-pensadores': [],
    'Folclore': [],
    'Contos': [],
    'Poesia': [],
    'Crônica': [],
    'Romance': ['Brasileiro', 'estrangeiro', 'juvenil'],
    'Ficção': [],
    'Quadrinhos': []
}

# Lista de todos os gêneros válidos
GENEROS_VALIDOS = list(GENEROS_SUBGENEROS.keys())

# Lista de todos os subgêneros válidos
SUBGENEROS_VALIDOS = []
for subgeneros in GENEROS_SUBGENEROS.values():
    SUBGENEROS_VALIDOS.extend(subgeneros)