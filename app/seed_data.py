# Dados do catálogo. Mantemos apenas receitas que aparecem de fato
# nos desenhos. As imagens são prints dos episódios (veja CENAS no final).

DESENHOS = [
    ("Bob Esponja", "🧽", "#f2b705"),
    ("Os Simpsons", "🍩", "#3aa0e8"),
    ("Naruto", "🍜", "#ff7a00"),
    ("Hora de Aventura", "🥓", "#2bb3c0"),
]

# (desenho, titulo, descricao, tempo_min, porcoes, dificuldade, ingredientes, preparo)
RECEITAS = [
    ("Bob Esponja", "Hambúrguer de Siri",
     "O hambúrguer gigante e exagerado que aparece em cenas do fundo do mar, com cara de desenho e muito sabor.",
     25, 2, "Fácil",
     """2 pães de hambúrguer
2 hambúrgueres de carne (120 g cada)
2 fatias de queijo
Alface, tomate e cebola fatiados
Picles a gosto
Ketchup e mostarda""",
     """Grelhe os hambúrgueres por 4 minutos de cada lado.
Coloque o queijo por cima no final para derreter.
Toste levemente os pães na frigideira.
Monte: pão, alface, hambúrguer com queijo, tomate, cebola, picles e molhos.
Sirva ainda quentinho."""),

    ("Os Simpsons", "Cachorro-quente Krusty",
     "O cachorro-quente de TV que aparece em destaque no episódio, com molho e pães bem recheados.",
     20, 4, "Fácil",
     """4 pães de cachorro-quente
4 salsichas
Mostarda e ketchup
Milho e ervilha
Batata palha
Cebola picada""",
     """Cozinhe as salsichas em água fervente por 5 minutos.
Aqueça levemente os pães.
Coloque a salsicha no pão, acrescente milho, ervilha e cebola.
Finalize com molhos e muita batata palha."""),

    ("Os Simpsons", "Donut Rosa do Homer",
     "A rosquinha rosa com glacê que Homer segura com a expressão de quem já sabe que é a melhor coisa da cozinha.",
     40, 8, "Média",
     """2 xícaras de farinha de trigo
1/2 xícara de açúcar
1 colher (sopa) de fermento
1/2 xícara de leite
2 ovos
1/4 xícara de óleo
1 colher (chá) de baunilha
Cobertura: 1 xícara de açúcar de confeiteiro, 2 colheres (sopa) de leite e corante rosa
Granulado colorido""",
     """Preaqueça o forno a 180 °C.
Misture todos os ingredientes da massa até ficar homogênea.
Coloque em forma de donut untada e asse por 12 a 15 minutos.
Misture o açúcar de confeiteiro, o leite e o corante para fazer a cobertura.
Mergulhe os donuts frios na cobertura e finalize com granulado."""),

    ("Naruto", "Ramen Ichiraku Caseiro",
     "A tigela enorme de ramen com ovos, massa e legumes que aparece na cena clássica do Naruto.",
     35, 2, "Média",
     """200 g de macarrão para lámen
1 litro de caldo de frango
2 colheres (sopa) de shoyu
1 colher (chá) de óleo de gergelim
2 ovos cozidos
Fatias de frango ou porco cozido
Cebolinha e nori""",
     """Aqueça o caldo com o shoyu e o óleo de gergelim.
Cozinhe o macarrão em outra panela, conforme a embalagem, e escorra.
Divida o macarrão em duas tigelas e cubra com o caldo quente.
Finalize com ovo cortado ao meio, carne, cebolinha e nori."""),

    ("Hora de Aventura", "Panqueca de Bacon do Finn e Jake",
     "A panqueca hot da dupla com bacon na frigideira, como aparece no episódio em forma de cena icônica.",
     25, 3, "Fácil",
     """1 xícara de farinha de trigo
1 colher (sopa) de fermento
1 colher (sopa) de açúcar
1 ovo
3/4 xícara de leite
6 fatias de bacon
Mel ou xarope de bordo""",
     """Misture a farinha, o fermento, o açúcar, o ovo e o leite.
Frite o bacon por 2 minutos em frigideira antiaderente, sem deixar crocante.
Despeje a massa por cima do bacon na própria frigideira.
Vire quando surgirem bolhas e doure o outro lado.
Sirva com mel."""),
]


# Cena do desenho em que cada receita aparece (chave = título da receita).
# Estes dados NÃO ficam no banco: são só informação de exibição, então não
# exigem migração. A imagem em si é um arquivo que você salva em
# app/static/images/cenas/<slug-do-titulo>.jpg (veja o README dessa pasta).
#   episodio: temporada/episódio onde o prato aparece
#   cena:     o que acontece na cena (também serve de texto alternativo)
#   credito:  dono dos direitos da imagem
CENAS = {
    "Hambúrguer de Siri": {
        "episodio": "T1E1 “Help Wanted”",
        "cena": "Bob Esponja prepara os primeiros Hambúrgueres de Siri na chapa do Siri Cascudo.",
        "credito": "Nickelodeon (Paramount)",
    },
    "Cachorro-quente Krusty": {
        "episodio": "T28 “Fatzcarraldo”",
        "cena": "Homer come cachorros-quentes com chili na carrocinha do Deuce, que o Krusty compra.",
        "credito": "20th Television (Disney)",
    },
    "Donut Rosa do Homer": {
        "episodio": "T7E6 “Treehouse of Horror VI”",
        "cena": "Homer com a rosquinha colossal da Lard Lad Donuts.",
        "credito": "20th Television (Disney)",
    },
    "Ramen Ichiraku Caseiro": {
        "episodio": "Ep. 1 “Enter: Naruto Uzumaki!”",
        "cena": "Iruka leva Naruto para comer ramen no Ichiraku.",
        "credito": "Masashi Kishimoto / Shueisha, TV Tokyo, Pierrot",
    },
    "Panqueca de Bacon do Finn e Jake": {
        "episodio": "T4E16 “Burning Low”",
        "cena": "Jake faz panquecas de bacon e canta a música “Bacon Pancakes”.",
        "credito": "Cartoon Network (Warner Bros. Discovery)",
    },
}
