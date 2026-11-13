import os
import re
import time
import socket
import sqlite3
import unicodedata
from urllib.parse import quote

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

from flask import Flask, request, redirect, jsonify, render_template, abort, send_from_directory
from werkzeug.utils import secure_filename

from seed_data import DESENHOS, RECEITAS, CENAS

app = Flask(__name__)


@app.route('/static')
@app.route('/static/')
def pagina_estatica():
    return send_from_directory(app.static_folder, 'index.html')


SQLITE_DB = os.path.join(os.path.dirname(__file__), "receitas.db")


def db_backend():
    if os.getenv("USE_SQLITE") == "1":
        return "sqlite"
    if psycopg2 is None:
        return "sqlite"
    try:
        con = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            dbname=os.getenv("DB_NAME", "receitas"),
            user=os.getenv("DB_USER", "receitas"),
            password=os.getenv("DB_PASSWORD", "receitas123"),
            connect_timeout=3,
        )
        con.close()
        return "postgres"
    except Exception:
        return "sqlite"


DB_BACKEND = db_backend()

# Prints dos episódios ficam em static/images/cenas/<slug-do-titulo>.<ext>
CENAS_DIR = os.path.join(os.path.dirname(__file__), "static", "images", "cenas")
STATIC_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "static", "images")
UPLOAD_IMAGES_DIR = os.path.join(STATIC_IMAGES_DIR, "manual")
EXTENSOES_CENA = ("jpg", "jpeg", "png", "webp")
EXTENSOES_IMAGEM = ("jpg", "jpeg", "png", "webp", "svg", "gif")


def slugify(texto):
    """'Hambúrguer de Siri' -> 'hamburguer-de-siri' (nome do arquivo da cena)."""
    ascii_ = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")


# Mesmos dados de CENAS, mas indexados pelo slug (ignora maiúsculas e acentos).
CENAS_POR_SLUG = {slugify(titulo): cena for titulo, cena in CENAS.items()}


def listar_imagens_disponiveis():
    """Lista imagens já salvas em /static/images para uso no cadastro."""
    imagens = []
    for raiz, _, arquivos in os.walk(STATIC_IMAGES_DIR):
        for nome in sorted(arquivos):
            ext = nome.rsplit(".", 1)[-1].lower()
            if ext not in EXTENSOES_IMAGEM:
                continue
            caminho = os.path.relpath(os.path.join(raiz, nome), os.path.join(os.path.dirname(__file__), "static"))
            imagens.append("/" + caminho.replace(os.sep, "/"))
    return sorted(set(imagens))


def normalizar_imagem_url(imagem):
    """Normaliza uma referência de imagem em /static/images para URL válida."""
    if not imagem:
        return None
    valor = imagem.strip().replace("\\", "/")
    if not valor:
        return None

    if valor.startswith("/"):
        valor = valor.lstrip("/")
    if valor.startswith("static/"):
        valor = valor[len("static/"):]
    caminho = os.path.join("static", valor)
    abs_path = os.path.join(os.path.dirname(__file__), caminho)
    if os.path.isfile(abs_path):
        return "/" + caminho.replace(os.sep, "/")

    for raiz, _, arquivos in os.walk(STATIC_IMAGES_DIR):
        if valor in arquivos:
            rel = os.path.relpath(os.path.join(raiz, valor), os.path.join(os.path.dirname(__file__), "static"))
            return "/" + rel.replace(os.sep, "/")
    return None


def salvar_imagem_upload(arquivo, titulo):
    """Salva um arquivo de imagem enviado pelo formulário na pasta estática."""
    if not arquivo or not getattr(arquivo, "filename", None):
        return None

    nome_original = secure_filename(arquivo.filename)
    if not nome_original:
        return None

    ext = os.path.splitext(nome_original)[1].lower()
    if ext not in {"." + e for e in EXTENSOES_IMAGEM}:
        return None

    os.makedirs(UPLOAD_IMAGES_DIR, exist_ok=True)
    nome_final = "%s%s" % (slugify(titulo), ext)
    caminho = os.path.join(UPLOAD_IMAGES_DIR, nome_final)
    if os.path.exists(caminho):
        base, ext2 = os.path.splitext(nome_final)
        contador = 1
        while os.path.exists(os.path.join(UPLOAD_IMAGES_DIR, "%s-%d%s" % (base, contador, ext2))):
            contador += 1
        nome_final = "%s-%d%s" % (base, contador, ext2)
        caminho = os.path.join(UPLOAD_IMAGES_DIR, nome_final)

    arquivo.save(caminho)
    return "/static/images/manual/%s" % nome_final


def imagem_receita(titulo, imagem=None):
    """URL da imagem da receita, preferindo a pasta de cenas e depois os assets do static."""
    url = normalizar_imagem_url(imagem) if imagem else None
    if url:
        return url

    slug = slugify(titulo)
    title_tokens = {p for p in re.split(r"[^a-z0-9]+", slug) if p}

    for ext in EXTENSOES_CENA:
        if os.path.isfile(os.path.join(CENAS_DIR, "%s.%s" % (slug, ext))):
            return "/static/images/cenas/%s.%s" % (slug, ext)

    for raiz, _, arquivos in os.walk(STATIC_IMAGES_DIR):
        for nome in sorted(arquivos):
            ext = nome.rsplit(".", 1)[-1].lower()
            if ext not in EXTENSOES_IMAGEM:
                continue
            stem = os.path.splitext(nome)[0]
            stem_tokens = {p for p in re.split(r"[^a-z0-9]+", slugify(stem)) if p}
            if not stem_tokens:
                continue
            if stem_tokens & title_tokens or stem_tokens.issubset(title_tokens) or title_tokens.issubset(stem_tokens):
                static_root = os.path.join(os.path.dirname(__file__), "static")
                caminho_absoluto = os.path.abspath(os.path.join(raiz, nome))
                try:
                    if os.path.commonpath([os.path.abspath(static_root), caminho_absoluto]) == os.path.abspath(static_root):
                        rel = os.path.relpath(caminho_absoluto, static_root)
                        return "/static/" + rel.replace(os.sep, "/")
                except ValueError:
                    pass
                return "/static/images/%s" % nome

    return None


def com_cena(r):
    """Anexa à receita a imagem da cena (ou None) e os dados do episódio."""
    r["imagem"] = r.get("imagem") or imagem_receita(r["titulo"])
    r["cena"] = CENAS_POR_SLUG.get(slugify(r["titulo"]))
    return r


def conectar():
    if DB_BACKEND == "sqlite" or psycopg2 is None:
        con = sqlite3.connect(SQLITE_DB)
        con.row_factory = sqlite3.Row
        return con

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        dbname=os.getenv("DB_NAME", "receitas"),
        user=os.getenv("DB_USER", "receitas"),
        password=os.getenv("DB_PASSWORD", "receitas123"),
        connect_timeout=3,
    )


def adaptar_sql_sqlite(sql, params=None):
    if params is None:
        params = ()
    query = sql.replace("ILIKE", "LIKE")
    query = query.replace("%s", "?")
    return query, tuple(params)


def consulta(sql, params=None, buscar=False):
    con = conectar()
    try:
        if DB_BACKEND == "sqlite":
            sql, params = adaptar_sql_sqlite(sql, params)
            with con:
                cur = con.cursor()
                cur.execute(sql, params or ())
                if buscar:
                    return [dict(row) for row in cur.fetchall()]
                return None

        with con:
            with con.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                if buscar:
                    return cur.fetchall()
    finally:
        con.close()


def obter_ou_criar_desenho(desenho_id=None, nome=None, emoji=None, cor=None):
    """Retorna o id do desenho selecionado ou cria um novo se houver nome."""
    nome = (nome or "").strip()
    if nome:
        existente = consulta("SELECT id FROM desenhos WHERE nome = ?", (nome,), buscar=True)
        if existente:
            return existente[0]["id"]
        default_emoji = (emoji or "🎨").strip() or "🎨"
        default_cor = (cor or "#7c3aed").strip() or "#7c3aed"
        if DB_BACKEND == "sqlite":
            consulta(
                "INSERT INTO desenhos (nome, emoji, cor) VALUES (?, ?, ?)",
                (nome, default_emoji, default_cor),
                buscar=False,
            )
        else:
            consulta(
                "INSERT INTO desenhos (nome, emoji, cor) VALUES (%s, %s, %s)",
                (nome, default_emoji, default_cor),
                buscar=False,
            )
        existente = consulta("SELECT id FROM desenhos WHERE nome = ?", (nome,), buscar=True)
        if existente:
            return existente[0]["id"]

    if desenho_id is None or str(desenho_id).strip() == "":
        return None
    try:
        return int(desenho_id)
    except (TypeError, ValueError):
        return None


def iniciar_banco():
    """Cria tabelas e carrega o catálogo apenas quando o banco está vazio.
    Isso evita que receitas removidas voltem ao reiniciar o app."""
    for _ in range(40):
        try:
            con = conectar()
            try:
                with con:
                    cur = con.cursor()
                    if DB_BACKEND == "postgres":
                        cur.execute("SELECT pg_advisory_xact_lock(42)")
                        cur.execute("""CREATE TABLE IF NOT EXISTS desenhos (
                                        id SERIAL PRIMARY KEY,
                                        nome TEXT UNIQUE NOT NULL,
                                        emoji TEXT NOT NULL,
                                        cor TEXT NOT NULL)""")
                        cur.execute("""CREATE TABLE IF NOT EXISTS receitas (
                                        id SERIAL PRIMARY KEY,
                                        desenho_id INT NOT NULL REFERENCES desenhos(id),
                                        titulo TEXT UNIQUE NOT NULL,
                                        descricao TEXT NOT NULL,
                                        tempo_min INT NOT NULL,
                                        porcoes INT NOT NULL,
                                        dificuldade TEXT NOT NULL,
                                        ingredientes TEXT NOT NULL,
                                        preparo TEXT NOT NULL,
                                        imagem TEXT,
                                        curtidas INT NOT NULL DEFAULT 0)""")
                    else:
                        cur.execute("""CREATE TABLE IF NOT EXISTS desenhos (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        nome TEXT UNIQUE NOT NULL,
                                        emoji TEXT NOT NULL,
                                        cor TEXT NOT NULL)""")
                        cur.execute("""CREATE TABLE IF NOT EXISTS receitas (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        desenho_id INTEGER NOT NULL,
                                        titulo TEXT UNIQUE NOT NULL,
                                        descricao TEXT NOT NULL,
                                        tempo_min INTEGER NOT NULL,
                                        porcoes INTEGER NOT NULL,
                                        dificuldade TEXT NOT NULL,
                                        ingredientes TEXT NOT NULL,
                                        preparo TEXT NOT NULL,
                                        imagem TEXT,
                                        curtidas INTEGER NOT NULL DEFAULT 0,
                                        FOREIGN KEY(desenho_id) REFERENCES desenhos(id))""")

                    if DB_BACKEND == "postgres":
                        cur.execute("ALTER TABLE receitas ADD COLUMN IF NOT EXISTS imagem TEXT")
                    else:
                        try:
                            cur.execute("ALTER TABLE receitas ADD COLUMN imagem TEXT")
                        except sqlite3.OperationalError:
                            pass

                    total_desenhos = cur.execute("SELECT COUNT(*) FROM desenhos").fetchone()[0]
                    total_receitas = cur.execute("SELECT COUNT(*) FROM receitas").fetchone()[0]
                    if total_desenhos > 0 or total_receitas > 0:
                        return

                    if DB_BACKEND == "sqlite":
                        for nome, emoji, cor in DESENHOS:
                            cur.execute("INSERT OR IGNORE INTO desenhos (nome, emoji, cor) VALUES (?, ?, ?)",
                                        (nome, emoji, cor))
                        for r in RECEITAS:
                            cur.execute(
                                "INSERT OR IGNORE INTO receitas (desenho_id, titulo, descricao, tempo_min, "
                                "porcoes, dificuldade, ingredientes, preparo) "
                                "VALUES ((SELECT id FROM desenhos WHERE nome = ?), ?, ?, ?, ?, ?, ?, ?)",
                                (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
                    else:
                        for nome, emoji, cor in DESENHOS:
                            cur.execute("INSERT INTO desenhos (nome, emoji, cor) VALUES (%s,%s,%s) "
                                        "ON CONFLICT (nome) DO NOTHING", (nome, emoji, cor))
                        for r in RECEITAS:
                            cur.execute(
                                "INSERT INTO receitas (desenho_id, titulo, descricao, tempo_min, "
                                "porcoes, dificuldade, ingredientes, preparo) "
                                "VALUES ((SELECT id FROM desenhos WHERE nome=%s), %s,%s,%s,%s,%s,%s,%s) "
                                "ON CONFLICT (titulo) DO NOTHING", r)
            finally:
                con.close()
            return
        except Exception:
            time.sleep(2)


@app.context_processor
def globais():
    return {"pod": socket.gethostname()}


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    d = request.args.get("desenho", "")
    sql = ("SELECT r.*, d.nome AS desenho, d.emoji, d.cor FROM receitas r "
           "JOIN desenhos d ON d.id = r.desenho_id WHERE 1=1")
    params = []
    if q:
        if DB_BACKEND == "sqlite":
            sql += " AND (LOWER(r.titulo) LIKE LOWER(?) OR LOWER(r.descricao) LIKE LOWER(?))"
        else:
            sql += " AND (r.titulo ILIKE %s OR r.descricao ILIKE %s)"
        params += ["%" + q + "%", "%" + q + "%"]
    if d.isdigit():
        sql += " AND d.id = %s"
        params.append(int(d))
    sql += " ORDER BY d.nome, r.titulo"
    receitas = consulta(sql, tuple(params), buscar=True)
    for r in receitas:
        com_cena(r)
    desenhos = consulta("SELECT * FROM desenhos ORDER BY nome", buscar=True)
    return render_template("index.html", receitas=receitas, desenhos=desenhos, q=q, d=d)


@app.route("/receita/<int:rid>")
def receita(rid):
    rows = consulta(
        "SELECT r.*, d.nome AS desenho, d.emoji, d.cor FROM receitas r "
        "JOIN desenhos d ON d.id = r.desenho_id WHERE r.id = %s",
        (rid,),
        buscar=True,
    )
    if not rows:
        abort(404)
    r = com_cena(rows[0])
    return render_template("receita.html", r=r,
                           ingredientes=r["ingredientes"].splitlines(),
                           passos=r["preparo"].splitlines())


@app.route("/receita/<int:rid>/curtir", methods=["POST"])
def curtir(rid):
    consulta("UPDATE receitas SET curtidas = curtidas + 1 WHERE id = %s", (rid,))
    return redirect("/receita/%d" % rid)


@app.route("/receita/<int:rid>/remover", methods=["POST"])
def remover_receita(rid):
    receita = consulta(
        "SELECT r.*, d.id AS desenho_id, d.nome AS desenho FROM receitas r JOIN desenhos d ON d.id = r.desenho_id WHERE r.id = %s",
        (rid,),
        buscar=True,
    )
    if not receita:
        abort(404)

    desenho_id = receita[0]["desenho_id"]
    consulta("DELETE FROM receitas WHERE id = %s", (rid,))

    restante = consulta(
        "SELECT id FROM receitas WHERE desenho_id = %s LIMIT 1",
        (desenho_id,),
        buscar=True,
    )
    if not restante:
        consulta("DELETE FROM desenhos WHERE id = %s", (desenho_id,))

    return redirect("/")


@app.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        f = request.form
        titulo = f["titulo"].strip()
        desenho_id = obter_ou_criar_desenho(
            f.get("desenho_id"),
            f.get("novo_desenho"),
            f.get("novo_emoji"),
            f.get("nova_cor"),
        )
        if desenho_id is None:
            desenhos = consulta("SELECT * FROM desenhos ORDER BY nome", buscar=True)
            return render_template(
                "nova.html",
                desenhos=desenhos,
                imagens_disponiveis=listar_imagens_disponiveis(),
                erro="Selecione um desenho existente ou crie um novo.",
            )

        imagem_url = salvar_imagem_upload(request.files.get("arquivo_imagem"), titulo)
        if not imagem_url:
            imagem_url = normalizar_imagem_url(f.get("imagem")) or imagem_receita(titulo)

        if DB_BACKEND == "sqlite":
            consulta(
                "INSERT INTO receitas (desenho_id, titulo, descricao, tempo_min, porcoes, "
                "dificuldade, ingredientes, preparo, imagem) VALUES (?,?,?,?,?,?,?,?,?)",
                (desenho_id, titulo, f["descricao"].strip(),
                 max(1, int(f["tempo_min"])), max(1, int(f["porcoes"])), f["dificuldade"],
                 f["ingredientes"].strip(), f["preparo"].strip(), imagem_url), buscar=False)
            row = consulta("SELECT id FROM receitas ORDER BY id DESC LIMIT 1", buscar=True)
            return redirect("/receita/%d" % row[0]["id"])

        rows = consulta(
            "INSERT INTO receitas (desenho_id, titulo, descricao, tempo_min, porcoes, "
            "dificuldade, ingredientes, preparo, imagem) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (desenho_id, titulo, f["descricao"].strip(),
             max(1, int(f["tempo_min"])), max(1, int(f["porcoes"])), f["dificuldade"],
             f["ingredientes"].strip(), f["preparo"].strip(), imagem_url), buscar=True)
        return redirect("/receita/%d" % rows[0]["id"])
    desenhos = consulta("SELECT * FROM desenhos ORDER BY nome", buscar=True)
    return render_template("nova.html", desenhos=desenhos, imagens_disponiveis=listar_imagens_disponiveis())


@app.route("/receita/<int:rid>/editar", methods=["GET", "POST"])
def editar_receita(rid):
    rows = consulta(
        "SELECT r.*, d.nome AS desenho, d.emoji, d.cor FROM receitas r "
        "JOIN desenhos d ON d.id = r.desenho_id WHERE r.id = %s",
        (rid,),
        buscar=True,
    )
    if not rows:
        abort(404)
    receita = rows[0]

    if request.method == "POST":
        f = request.form
        titulo = f["titulo"].strip()
        desenho_id = obter_ou_criar_desenho(
            f.get("desenho_id"),
            f.get("novo_desenho"),
            f.get("novo_emoji"),
            f.get("nova_cor"),
        )
        if desenho_id is None:
            desenhos = consulta("SELECT * FROM desenhos ORDER BY nome", buscar=True)
            return render_template(
                "nova.html",
                desenhos=desenhos,
                imagens_disponiveis=listar_imagens_disponiveis(),
                receita=receita,
                editando=True,
                erro="Selecione um desenho existente ou crie um novo.",
            )

        imagem_url = salvar_imagem_upload(request.files.get("arquivo_imagem"), titulo)
        if not imagem_url:
            imagem_url = normalizar_imagem_url(f.get("imagem")) or imagem_receita(titulo, receita.get("imagem"))

        if DB_BACKEND == "sqlite":
            consulta(
                "UPDATE receitas SET desenho_id = ?, titulo = ?, descricao = ?, tempo_min = ?, "
                "porcoes = ?, dificuldade = ?, ingredientes = ?, preparo = ?, imagem = ? WHERE id = ?",
                (desenho_id, titulo, f["descricao"].strip(),
                 max(1, int(f["tempo_min"])), max(1, int(f["porcoes"])), f["dificuldade"],
                 f["ingredientes"].strip(), f["preparo"].strip(), imagem_url, rid),
                buscar=False,
            )
        else:
            consulta(
                "UPDATE receitas SET desenho_id = %s, titulo = %s, descricao = %s, tempo_min = %s, "
                "porcoes = %s, dificuldade = %s, ingredientes = %s, preparo = %s, imagem = %s WHERE id = %s",
                (desenho_id, titulo, f["descricao"].strip(),
                 max(1, int(f["tempo_min"])), max(1, int(f["porcoes"])), f["dificuldade"],
                 f["ingredientes"].strip(), f["preparo"].strip(), imagem_url, rid),
                buscar=False,
            )
        return redirect("/receita/%d" % rid)

    desenhos = consulta("SELECT * FROM desenhos ORDER BY nome", buscar=True)
    return render_template(
        "nova.html",
        desenhos=desenhos,
        imagens_disponiveis=listar_imagens_disponiveis(),
        receita=receita,
        editando=True,
    )


@app.errorhandler(404)
def nao_encontrado(_erro):
    return render_template("404.html"), 404


@app.route("/api/receitas")
def api_receitas():
    dados = consulta("SELECT r.id, r.titulo, d.nome AS desenho, r.tempo_min, r.porcoes, "
                     "r.dificuldade, r.curtidas FROM receitas r JOIN desenhos d "
                     "ON d.id = r.desenho_id ORDER BY r.id", buscar=True)
    return jsonify(dados)


@app.route("/health")
def health():
    try:
        con = conectar()
        con.close()
        return "ok", 200
    except Exception as e:
        return f"database error: {str(e)}", 500


iniciar_banco()
