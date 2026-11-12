import importlib
import os
import sys
from unittest.mock import patch


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP_DIR = os.path.join(ROOT, 'app')
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)


def carregar_app():
    os.environ['USE_SQLITE'] = '1'
    import app as app_module
    return importlib.reload(app_module)


def test_sqlite_initialization_works():
    db_path = os.path.join(APP_DIR, 'receitas.db')
    if os.path.exists(db_path):
        os.remove(db_path)

    carregar_app()
    with patch('time.sleep', side_effect=AssertionError('unexpected retry loop')):
        app_module = carregar_app()

    assert app_module.DB_BACKEND == 'sqlite'
    client = app_module.app.test_client()
    assert client.get('/health').status_code == 200
    assert client.get('/').status_code == 200
    assert client.get('/receita/1').status_code == 200
    assert client.get('/receita/9999').status_code == 404


def test_curtir_incrementa():
    app_module = carregar_app()
    client = app_module.app.test_client()
    antes = app_module.consulta('SELECT curtidas FROM receitas WHERE id = %s', (1,), buscar=True)[0]['curtidas']
    assert client.post('/receita/1/curtir').status_code == 302
    depois = app_module.consulta('SELECT curtidas FROM receitas WHERE id = %s', (1,), buscar=True)[0]['curtidas']
    assert depois == antes + 1


def test_slugify():
    app_module = carregar_app()
    assert app_module.slugify('Hambúrguer de Siri') == 'hamburguer-de-siri'
    assert app_module.slugify('Cachorro-quente Krusty') == 'cachorro-quente-krusty'


def test_nova_receita_cria_novo_desenho():
    app_module = carregar_app()
    client = app_module.app.test_client()
    resp = client.post('/nova', data={
        'desenho_id': '999',
        'novo_desenho': 'Dragon Ball',
        'novo_emoji': '🐉',
        'nova_cor': '#ff8a00',
        'titulo': 'Receita de Teste do Dragon Ball',
        'descricao': 'Receita nova',
        'tempo_min': '22',
        'porcoes': '2',
        'dificuldade': 'Média',
        'ingredientes': '1 ovo\n2 colheres de farinha',
        'preparo': 'Misture\nSirva',
    }, follow_redirects=True)
    assert resp.status_code == 200
    desenho = app_module.consulta('SELECT nome, emoji, cor FROM desenhos WHERE nome = ?', ('Dragon Ball',), buscar=True)
    assert desenho and desenho[0]['nome'] == 'Dragon Ball'
    assert desenho[0]['emoji'] == '🐉'


def test_editar_receita_atualiza_dados():
    app_module = carregar_app()
    client = app_module.app.test_client()
    resp = client.post('/receita/1/editar', data={
        'titulo': 'Hambúrguer de Siri',
        'desenho_id': '1',
        'novo_desenho': '',
        'descricao': 'Versão atualizada do hambúrguer clássico',
        'tempo_min': '35',
        'porcoes': '3',
        'dificuldade': 'Média',
        'ingredientes': '2 pães\n2 hambúrgueres\nQueijo',
        'preparo': 'Prep 1\nPrep 2',
    }, follow_redirects=True)
    assert resp.status_code == 200
    row = app_module.consulta('SELECT descricao, tempo_min, porcoes, dificuldade FROM receitas WHERE id = ?', (1,), buscar=True)
    assert row[0]['descricao'] == 'Versão atualizada do hambúrguer clássico'
    assert row[0]['tempo_min'] == 35
    assert row[0]['porcoes'] == 3


def test_remover_receita_exclui_registro():
    app_module = carregar_app()
    client = app_module.app.test_client()
    app_module.consulta('INSERT INTO receitas (desenho_id, titulo, descricao, tempo_min, porcoes, dificuldade, ingredientes, preparo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       (1, 'Receita para remover', 'Temporária', 10, 2, 'Fácil', '1 item', 'Passo 1'), buscar=False)
    row = app_module.consulta('SELECT id FROM receitas WHERE titulo = ?', ('Receita para remover',), buscar=True)
    rid = row[0]['id']

    resp = client.post(f'/receita/{rid}/remover', follow_redirects=True)
    assert resp.status_code == 200
    assert app_module.consulta('SELECT id FROM receitas WHERE id = ?', (rid,), buscar=True) == []


def test_sem_arquivo_nao_usa_imagem(tmp_path):
    app_module = carregar_app()
    with patch.object(app_module, 'CENAS_DIR', str(tmp_path)), patch.object(app_module, 'STATIC_IMAGES_DIR', str(tmp_path)):
        assert app_module.imagem_receita('Hambúrguer de Siri') is None


def test_usa_print_do_episodio_quando_existe(tmp_path):
    app_module = carregar_app()
    (tmp_path / 'hamburguer-de-siri.png').write_bytes(b'x')
    with patch.object(app_module, 'CENAS_DIR', str(tmp_path)), patch.object(app_module, 'STATIC_IMAGES_DIR', str(tmp_path)):
        url = app_module.imagem_receita('hambúrguer de siri')
    assert url == '/static/images/cenas/hamburguer-de-siri.png'


def test_nova_receita_pode_usar_imagem_ja_cadastrada():
    app_module = carregar_app()
    client = app_module.app.test_client()
    titulo = 'Receita de Teste com Imagem'
    resp = client.post('/nova', data={
        'desenho_id': '1',
        'titulo': titulo,
        'descricao': 'Receita de teste',
        'tempo_min': '25',
        'porcoes': '2',
        'dificuldade': 'Fácil',
        'ingredientes': '1 ovo\n2 colheres de farinha',
        'preparo': 'Misture tudo\nSirva',
        'imagem': '/static/images/hamburguer-siri.png',
    }, follow_redirects=True)
    assert resp.status_code == 200
    row = app_module.consulta('SELECT imagem FROM receitas WHERE titulo = ?', (titulo,), buscar=True)
    assert row and row[0]['imagem'] == '/static/images/hamburguer-siri.png'


def test_usa_imagem_do_static_quando_o_arquivo_nao_seguititulo_exato(tmp_path):
    app_module = carregar_app()
    (tmp_path / 'hamburguer-siri.png').write_bytes(b'x')
    with patch.object(app_module, 'STATIC_IMAGES_DIR', str(tmp_path)):
        url = app_module.imagem_receita('Hambúrguer de Siri')
    assert url == '/static/images/hamburguer-siri.png'


def test_toda_receita_do_catalogo_tem_dados_de_cena():
    app_module = carregar_app()
    from seed_data import RECEITAS
    for r in RECEITAS:
        assert app_module.slugify(r[1]) in app_module.CENAS_POR_SLUG, r[1]
