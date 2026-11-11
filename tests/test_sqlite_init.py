import importlib
import os
import sys
from unittest.mock import patch


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP_DIR = os.path.join(ROOT, 'app')
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)


def test_sqlite_initialization_works():
    db_path = os.path.join(APP_DIR, 'receitas.db')
    if os.path.exists(db_path):
        os.remove(db_path)

    os.environ['USE_SQLITE'] = '1'

    import app as app_module
    importlib.reload(app_module)

    with patch('time.sleep', side_effect=AssertionError('unexpected retry loop')):
        importlib.reload(app_module)

    assert app_module.DB_BACKEND == 'sqlite'
    client = app_module.app.test_client()
    assert client.get('/health').status_code == 200
    assert client.get('/receita/1').status_code == 200


def test_receita_uses_cartoon_style_image():
    os.environ['USE_SQLITE'] = '1'
    import app as app_module
    importlib.reload(app_module)

    image_url = app_module.imagem_receita('hambúrguer de siri', 'Bob Esponja')
    assert image_url.startswith('data:image/svg+xml')
    assert 'unsplash.com' not in image_url.lower()
