# Gêneros e subgêneros para validação e API
GENEROS_SUBGENEROS = {
    'literatura-brasileira': [
        'romantismo', 'realismo', 'naturalismo', 'parnasianismo', 'simbolismo',
        'pré-modernismo', 'modernismo', 'pós-modernismo', 'literatura contemporânea',
        'literatura colonial', 'barroco', 'arcadismo', 'literatura de cordel'
    ],
    'literatura-estrangeira': [
        'literatura inglesa', 'literatura americana', 'literatura francesa', 'literatura alemã',
        'literatura russa', 'literatura espanhola', 'literatura italiana', 'literatura japonesa',
        'literatura africana', 'literatura latino-americana', 'literatura portuguesa'
    ],
    'ficção': [
        'ficção científica', 'fantasia', 'terror', 'suspense', 'mistério', 'policial',
        'aventura', 'drama', 'romance', 'ficção histórica', 'ficção gótica',
        'realismo mágico', 'distopia', 'utopia', 'ficção urbana', 'western'
    ],
    'poesia': [
        'soneto', 'épico', 'lírico', 'dramático', 'elegia', 'ode', 'sátira',
        'haicai', 'trova', 'repente', 'slam', 'poesia concreta', 'poesia marginal'
    ],
    'teatro': [
        'tragédia', 'comédia', 'drama', 'auto', 'farsa', 'melodrama',
        'teatro épico', 'teatro do absurdo', 'monólogo', 'musical'
    ],
    'literatura-infantil': [
        'contos de fada', 'fábulas', 'lendas', 'mitos', 'aventura infantil',
        'educativo infantil', 'livro ilustrado', 'literatura de berço'
    ],
    'literatura-juvenil': [
        'romance juvenil', 'ficção juvenil', 'aventura juvenil', 'fantasia juvenil',
        'distopia juvenil', 'coming-of-age', 'young adult'
    ],
    'história': [
        'história do brasil', 'história mundial', 'história antiga', 'história medieval',
        'história moderna', 'história contemporânea', 'história local', 'historiografia'
    ],
    'geografia': [
        'geografia física', 'geografia humana', 'cartografia', 'geologia',
        'climatologia', 'geografia do brasil', 'geografia mundial'
    ],
    'ciências': [
        'física', 'química', 'biologia', 'matemática', 'astronomia',
        'ciências naturais', 'ecologia', 'meio ambiente', 'genética'
    ],
    'filosofia': [
        'filosofia antiga', 'filosofia medieval', 'filosofia moderna', 'filosofia contemporânea',
        'ética', 'lógica', 'metafísica', 'epistemologia', 'filosofia política'
    ],
    'religião': [
        'cristianismo', 'catolicismo', 'protestantismo', 'islamismo', 'judaísmo',
        'budismo', 'hinduísmo', 'religiões afro-brasileiras', 'teologia', 'espiritualidade'
    ],
    'artes': [
        'história da arte', 'pintura', 'escultura', 'arquitetura', 'fotografia',
        'cinema', 'teatro', 'dança', 'arte brasileira', 'arte contemporânea'
    ],
    'música': [
        'história da música', 'música clássica', 'música popular brasileira', 'jazz',
        'rock', 'música folclórica', 'teoria musical', 'instrumentos musicais'
    ],
    'educação': [
        'pedagogia', 'didática', 'psicologia educacional', 'educação infantil',
        'educação especial', 'educação de jovens e adultos', 'gestão escolar'
    ],
    'psicologia': [
        'psicologia geral', 'psicologia social', 'psicologia clínica', 'psicanálise',
        'psicologia cognitiva', 'psicologia do desenvolvimento', 'neuropsicologia'
    ],
    'sociologia': [
        'sociologia geral', 'sociologia brasileira', 'sociologia urbana', 'sociologia rural',
        'sociologia da educação', 'sociologia política', 'antropologia'
    ],
    'direito': [
        'direito constitucional', 'direito civil', 'direito penal', 'direito trabalhista',
        'direito administrativo', 'direito comercial', 'direitos humanos'
    ],
    'economia': [
        'microeconomia', 'macroeconomia', 'economia brasileira', 'economia mundial',
        'economia política', 'desenvolvimento econômico', 'finanças'
    ],
    'administração': [
        'administração geral', 'gestão de pessoas', 'marketing', 'finanças empresariais',
        'logística', 'empreendedorismo', 'administração pública'
    ],
    'tecnologia': [
        'informática', 'programação', 'inteligência artificial', 'robótica',
        'telecomunicações', 'engenharia de software', 'redes de computadores'
    ],
    'saúde': [
        'medicina', 'enfermagem', 'farmácia', 'odontologia', 'fisioterapia',
        'nutrição', 'saúde pública', 'anatomia', 'fisiologia'
    ],
    'esportes': [
        'educação física', 'futebol', 'basquete', 'vôlei', 'atletismo',
        'natação', 'artes marciais', 'esportes olímpicos', 'recreação'
    ],
    'culinária': [
        'culinária brasileira', 'culinária internacional', 'doces e sobremesas',
        'alimentação saudável', 'gastronomia', 'técnicas culinárias'
    ],
    'autoajuda': [
        'desenvolvimento pessoal', 'motivação', 'liderança', 'relacionamentos',
        'espiritualidade', 'mindfulness', 'produtividade', 'inteligência emocional'
    ],
    'biografia': [
        'biografia política', 'biografia artística', 'biografia científica',
        'autobiografia', 'memórias', 'personalidades brasileiras', 'personalidades mundiais'
    ],
    'referência': [
        'dicionário português', 'dicionário inglês', 'enciclopédia', 'atlas',
        'gramática', 'manual técnico', 'guia de estudo', 'almanaque'
    ],
    'quadrinhos': [
        'super-heróis', 'mangá', 'graphic novel', 'quadrinhos brasileiros',
        'quadrinhos europeus', 'quadrinhos infantis', 'webcomics'
    ],
    'humor': [
        'comédia', 'sátira', 'paródia', 'crônicas humorísticas',
        'stand-up comedy', 'humor brasileiro', 'cartuns'
    ]
}

# Lista de todos os gêneros válidos
GENEROS_VALIDOS = list(GENEROS_SUBGENEROS.keys())

# Lista de todos os subgêneros válidos
SUBGENEROS_VALIDOS = []
for subgeneros in GENEROS_SUBGENEROS.values():
    SUBGENEROS_VALIDOS.extend(subgeneros)