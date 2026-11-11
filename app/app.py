import os
import time
import socket
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, redirect, jsonify, render_template, abort

from seed_data import DESENHOS, RECEITAS

app = Flask(__name__)


def conectar():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        dbname=os.getenv("DB_NAME", "receitas"),
        user=os.getenv("DB_USER", "receitas"),
        password=os.getenv("DB_PASSWORD", "receitas123"),
        connect_timeout=3,
    )


def consulta(sql, params=None, buscar=False):
    con = conectar()
    try:
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
                    with con.cursor() as cur:
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
        sql += " AND (r.titulo ILIKE %s OR r.descricao ILIKE %s)"
        params += ["%" + q + "%", "%" + q + "%"]
    if d.isdigit():
        sql += " AND d.id = %s"
        params.append(int(d))
    sql += " ORDER BY d.nome, r.titulo"
    receitas = consulta(sql, tuple(params), buscar=True)
    desenhos = consulta("SELECT * FROM desenhos ORDER BY nome", buscar=True)
    return render_template("index.html", receitas=receitas, desenhos=desenhos, q=q, d=d)


@app.route("/receita/<int:rid>")
def receita(rid):
    rows = consulta("SELECT r.*, d.nome AS desenho, d.emoji, d.cor FROM receitas r "
                    "JOIN desenhos d ON d.id = r.desenho_id WHERE r.id = %s", (rid,), buscar=True)
    if not rows:
        abort(404)
    r = rows[0]
    return render_template("receita.html", r=r,
                           ingredientes=r["ingredientes"].splitlines(),
                           passos=r["preparo"].splitlines())


@app.route("/receita/<int:rid>/curtir", methods=["POST"])
def curtir(rid):
    consulta("UPDATE receitas SET curtidas = curtidas + 1 WHERE id = %s", (rid,))
    return redirect("/receita/%d" % rid)


@app.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        f = request.form
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
