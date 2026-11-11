# Dados iniciais do catalogo. Receitas escritas de forma original,
# apenas inspiradas nos desenhos animados.

DESENHOS = [
    ("Bob Esponja", "🧽", "#f2b705"),
    ("Os Simpsons", "🍩", "#3aa0e8"),
    ("Scooby-Doo", "🐶", "#8a5a2b"),
    ("Naruto", "🍜", "#ff7a00"),
    ("Pokémon", "⚪", "#e53935"),
    ("Tom e Jerry", "🧀", "#7c9a92"),
    ("Hora de Aventura", "🥓", "#2bb3c0"),
]

# (desenho, titulo, descricao, tempo_min, porcoes, dificuldade, ingredientes, preparo)
RECEITAS = [
    ("Bob Esponja", "Hambúrguer de Siri",
     "Inspirado no sanduíche mais famoso do fundo do mar. A fórmula secreta é caprichar nos ingredientes.",
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

    ("Bob Esponja", "Panqueca Quadrada",
     "Panquecas em formato de quadrado, com furinhos para absorver bastante mel.",
     20, 3, "Fácil",
     """1 xícara de farinha de trigo
1 colher (sopa) de fermento
1 colher (sopa) de açúcar
1 ovo
1 xícara de leite
1 colher (sopa) de manteiga derretida
Mel para servir""",
     """Misture os ingredientes secos e depois adicione o ovo, o leite e a manteiga.
Cozinhe a massa em frigideira untada, em fogo baixo, até dourar dos dois lados.
Apare as bordas com uma faca para deixar cada panqueca quadrada.
Faça furinhos com um palito, como uma esponja.
Empilhe e regue com mel."""),

    ("Bob Esponja", "Gelatina Azul do Fundo do Mar",
     "Sobremesa gelada com cor de oceano e cobertura de creme.",
     20, 6, "Fácil",
     """1 pacote de gelatina azul em pó
250 ml de água quente
250 ml de água fria
1 caixinha de creme de leite
2 colheres (sopa) de coco ralado""",
     """Dissolva a gelatina na água quente e acrescente a água fria.
Distribua em copos e leve à geladeira por 4 horas.
Misture o creme de leite com o coco ralado.
Cubra a gelatina firme com o creme e sirva gelada."""),

    ("Os Simpsons", "Donut Rosa do Homer",
     "Rosquinha assada com cobertura rosa e granulado colorido, sem fritura.",
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

    ("Os Simpsons", "Cachorro-quente Krusty",
     "Cachorro-quente completo, caprichado como o de um palhaço de TV.",
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

    ("Scooby-Doo", "Biscoito Scooby Snack",
     "Biscoitinhos de baunilha, mel e canela em formato de osso.",
     45, 20, "Média",
     """2 xícaras de farinha de trigo
1/2 xícara de manteiga em temperatura ambiente
1/3 xícara de açúcar mascavo
3 colheres (sopa) de mel
1 ovo
1 colher (chá) de canela
1 colher (chá) de baunilha""",
     """Misture a manteiga, o açúcar e o mel até formar um creme.
Adicione o ovo e a baunilha, depois a farinha e a canela.
Abra a massa com 5 mm de espessura e corte com cortador em formato de osso.
Asse a 175 °C por 10 a 12 minutos e deixe esfriar."""),

    ("Scooby-Doo", "Sanduíche Gigante do Salsicha",
     "Um sanduíche enorme em camadas, do jeito que só o Salsicha monta.",
     15, 2, "Fácil",
     """1 pão italiano grande
Presunto e queijo
Peito de peru
Alface e tomate
Maionese e mostarda
Ovo cozido fatiado
Picles""",
     """Corte o pão ao meio no sentido do comprimento.
Passe maionese e mostarda nas duas metades.
Faça camadas de presunto, queijo, peru, ovo, alface, tomate e picles.
Feche, corte em pedaços e sirva."""),

    ("Naruto", "Ramen Ichiraku Caseiro",
     "Versão simples do lámen de balcão, com caldo saboroso e ovo.",
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

    ("Naruto", "Dango Tricolor",
     "Bolinhos de arroz doces em três cores, com calda de shoyu.",
     40, 4, "Média",
     """1 xícara de farinha de arroz glutinoso (mochiko)
3/4 xícara de água morna
2 colheres (sopa) de açúcar
Corante rosa e matcha (ou corante verde)
Calda: 1/4 xícara de shoyu, 1/4 xícara de açúcar, 1/2 xícara de água, 1 colher (chá) de amido""",
     """Misture a farinha, o açúcar e a água até obter uma massa lisa.
Divida em 3 partes: uma rosa, uma branca e uma verde.
Faça bolinhas e cozinhe em água fervente até boiarem, cerca de 3 minutos.
Passe para água gelada, escorra e espete 3 bolinhas por palito.
Ferva os ingredientes da calda até engrossar e regue os dangos."""),

    ("Pokémon", "Onigiri do Treinador",
     "Bolinho de arroz em formato de triângulo, ótimo para levar na jornada.",
     25, 4, "Fácil",
     """2 xícaras de arroz japonês cozido
Sal
Folhas de nori
Recheio: atum com maionese, salmão ou ameixa""",
     """Molhe as mãos com água e sal.
Coloque arroz na palma, faça um buraco e adicione o recheio.
Feche e modele em formato de triângulo.
Envolva com uma tira de nori e sirva."""),

    ("Pokémon", "Cupcake Pokébola",
     "Cupcake de baunilha com cobertura que imita uma Pokébola.",
     50, 12, "Média",
     """1 1/2 xícara de farinha de trigo
1 xícara de açúcar
1/2 xícara de manteiga
2 ovos
1/2 xícara de leite
1 colher (sopa) de fermento
Glacê vermelho e branco
Chocolate derretido""",
     """Bata a manteiga com o açúcar e junte os ovos.
Alterne a farinha com o leite e finalize com o fermento.
Asse em forminhas a 180 °C por 20 minutos.
Cubra os cupcakes frios com glacê vermelho.
Faça um círculo branco e uma faixa de chocolate para formar a Pokébola."""),

    ("Tom e Jerry", "Queijo Suíço Empanado do Jerry",
     "Cubos de queijo empanados e crocantes, com furinhos como queijo suíço.",
     30, 4, "Média",
     """300 g de queijo muçarela ou coalho em cubos grandes
Farinha de trigo
2 ovos batidos
Farinha panko ou farinha de rosca
Óleo para fritar""",
     """Faça furos nos cubos de queijo com um descaroçador ou canudo grosso.
Leve ao congelador por 20 minutos.
Passe na farinha, no ovo e na farinha panko; repita ovo e panko para ficar bem crocante.
Frite em óleo quente até dourar ou asse na airfryer a 200 °C por 8 minutos."""),

    ("Hora de Aventura", "Panqueca de Bacon do Finn e Jake",
     "A famosa combinação de panqueca com bacon, tudo cozido junto.",
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
