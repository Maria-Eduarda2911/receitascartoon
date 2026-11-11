import os
import time
import socket
import sqlite3
from urllib.parse import quote

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

from flask import Flask, request, redirect, jsonify, render_template, abort

from seed_data import DESENHOS, RECEITAS

app = Flask(__name__)
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

IMAGENS_RECEITAS = {}


def _emoji_receita(titulo):
    texto = (titulo or "").lower()
    if any(p in texto for p in ["hambúrguer", "burger", "siri"]):
        return "🍔"
    if any(p in texto for p in ["donut", "rosa", "rosquinha"]):
        return "🍩"
    if any(p in texto for p in ["cachorro", "hot dog", "salsicha"]):
        return "🌭"
    if any(p in texto for p in ["ramen", "miojo", "macarrão"]):
        return "🍜"
    if any(p in texto for p in ["panqueca", "crepe", "bacon"]):
        return "🥞"
    if any(p in texto for p in ["gelatina", "sobremesa", "doce"]):
        return "🍮"
    if any(p in texto for p in ["biscoito", "cookie", "snack"]):
        return "🍪"
    if any(p in texto for p in ["sanduíche", "misto"]):
        return "🥪"
    if any(p in texto for p in ["onigiri", "arroz"]):
        return "🍙"
    if any(p in texto for p in ["cupcake", "bolo"]):
        return "🧁"
    if any(p in texto for p in ["dango", "bolinho", "tricolor"]):
        return "🍡"
    if any(p in texto for p in ["queijo", "cheese"]):
        return "🧀"
    return "🍽️"


def _paleta_receita(titulo, desenho=None):
    texto = (f"{titulo} {desenho or ''}").lower()
    paletas = {
        "bob esponja": ["#ffd166", "#ff6b6b", "#4ecdc4"],
        "os simpsons": ["#f7b267", "#f4845f", "#f35b7a"],
        "scooby-doo": ["#7bdff2", "#b2f7ef", "#ffc6ff"],
        "naruto": ["#ff7f50", "#ffb703", "#f94144"],
        "tom e jerry": ["#90be6d", "#f4a261", "#e76f51"],
        "pokemon": ["#6ec6ff", "#ffd166", "#90be6d"],
        "hora de aventura": ["#5eead4", "#a78bfa", "#f9a8d4"],
    }
    for nome, cores in paletas.items():
        if nome in texto:
            return cores
    if "hambúrguer" in texto or "burger" in texto:
        return ["#ffb703", "#ff7f50", "#fb8500"]
    if "donut" in texto or "rosa" in texto:
        return ["#ff9ecb", "#ff6bb5", "#ffd166"]
    if "ramen" in texto:
        return ["#f4a261", "#e76f51", "#2a9d8f"]
    if "panqueca" in texto:
        return ["#f9c74f", "#f9844a", "#f94144"]
    if "gelatina" in texto:
        return ["#7bdff2", "#b2f7ef", "#6c5ce7"]
    return ["#ffcc70", "#ff9f1c", "#ff6b6b"]


def imagem_receita(titulo, desenho=None):
    titulo_limpo = (titulo or "Receita").strip() or "Receita"
    emoji = _emoji_receita(titulo_limpo)
    cor1, cor2, cor3 = _paleta_receita(titulo_limpo, desenho)
    label = (desenho or "Receita").strip() or "Receita"
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">
      <defs>
        <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="{cor1}"/>
          <stop offset="55%" stop-color="{cor2}"/>
          <stop offset="100%" stop-color="{cor3}"/>
        </linearGradient>
      </defs>
      <rect width="1200" height="800" fill="url(#bg)"/>
      <circle cx="280" cy="220" r="150" fill="rgba(255,255,255,0.17)"/>
      <circle cx="980" cy="640" r="180" fill="rgba(255,255,255,0.12)"/>
      <circle cx="980" cy="180" r="120" fill="rgba(255,255,255,0.18)"/>
      <g>
        <rect x="210" y="180" width="780" height="420" rx="60" fill="rgba(255,255,255,0.18)" stroke="rgba(255,255,255,0.6)" stroke-width="8"/>
        <text x="600" y="400" text-anchor="middle" font-size="260" font-family="Arial, sans-serif">{emoji}</text>
      </g>
      <g>
        <rect x="200" y="610" width="800" height="110" rx="28" fill="rgba(28,20,45,0.28)"/>
        <text x="600" y="665" text-anchor="middle" font-size="52" font-weight="700" fill="#fffaf5" font-family="Arial, sans-serif">{titulo_limpo}</text>
        <text x="600" y="720" text-anchor="middle" font-size="28" fill="#fffaf5" opacity="0.9" font-family="Arial, sans-serif">{label}</text>
      </g>
    </svg>
    """.strip()
    return "data:image/svg+xml;charset=utf-8," + quote(svg)


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


def iniciar_banco():
    """Cria tabelas e carrega o catalogo. Tenta de novo ate o banco ficar pronto.
    O advisory lock evita conflito quando varios pods iniciam ao mesmo tempo."""
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
                                        curtidas INTEGER NOT NULL DEFAULT 0,
                                        FOREIGN KEY(desenho_id) REFERENCES desenhos(id))""")

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
        sql += " AND d.id = ?" if DB_BACKEND == "sqlite" else " AND d.id = %s"
        params.append(int(d)) if DB_BACKEND == "sqlite" else params.append(int(d))
    sql += " ORDER BY d.nome, r.titulo"
    receitas = consulta(sql, tuple(params), buscar=True)
    for r in receitas:
        r["imagem"] = imagem_receita(r["titulo"], r["desenho"])
    desenhos = consulta("SELECT * FROM desenhos ORDER BY nome", buscar=True)
    return render_template("index.html", receitas=receitas, desenhos=desenhos, q=q, d=d)


@app.route("/receita/<int:rid>")
def receita(rid):
    rows = consulta(
        "SELECT r.*, d.nome AS desenho, d.emoji, d.cor FROM receitas r "
        "JOIN desenhos d ON d.id = r.desenho_id WHERE r.id = ?",
        (rid,),
        buscar=True,
    )
    if not rows:
        abort(404)
    r = rows[0]
    r["imagem"] = imagem_receita(r["titulo"], r["desenho"])
    return render_template("receita.html", r=r,
                           ingredientes=r["ingredientes"].splitlines(),
                           passos=r["preparo"].splitlines())


@app.route("/receita/<int:rid>/curtir", methods=["POST"])
def curtir(rid):
    consulta("UPDATE receitas SET curtidas = curtidas + 1 WHERE id = ?", (rid,))
    return redirect("/receita/%d" % rid)


@app.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        f = request.form
        if DB_BACKEND == "sqlite":
            consulta(
                "INSERT INTO receitas (desenho_id, titulo, descricao, tempo_min, porcoes, "
                "dificuldade, ingredientes, preparo) VALUES (?,?,?,?,?,?,?,?)",
                (int(f["desenho_id"]), f["titulo"].strip(), f["descricao"].strip(),
                 max(1, int(f["tempo_min"])), max(1, int(f["porcoes"])), f["dificuldade"],
                 f["ingredientes"].strip(), f["preparo"].strip()), buscar=False)
            row = consulta("SELECT id FROM receitas ORDER BY id DESC LIMIT 1", buscar=True)
            return redirect("/receita/%d" % row[0]["id"])

        rows = consulta(
            "INSERT INTO receitas (desenho_id, titulo, descricao, tempo_min, porcoes, "
            "dificuldade, ingredientes, preparo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (int(f["desenho_id"]), f["titulo"].strip(), f["descricao"].strip(),
             max(1, int(f["tempo_min"])), max(1, int(f["porcoes"])), f["dificuldade"],
             f["ingredientes"].strip(), f["preparo"].strip()), buscar=True)
        return redirect("/receita/%d" % rows[0]["id"])
    desenhos = consulta("SELECT * FROM desenhos ORDER BY nome", buscar=True)
    return render_template("nova.html", desenhos=desenhos)


@app.route("/api/receitas")
def api_receitas():
    dados = consulta("SELECT r.id, r.titulo, d.nome AS desenho, r.tempo_min, r.porcoes, "
                     "r.dificuldade, r.curtidas FROM receitas r JOIN desenhos d "
                     "ON d.id = r.desenho_id ORDER BY r.id", buscar=True)
    return jsonify(dados)


@app.route("/health")
def health():
    return "ok"


iniciar_banco()
