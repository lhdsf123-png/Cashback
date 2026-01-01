from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "segredo123"  # chave para sessão

# Banco de dados em memória
usuarios = {}  # {username: {"senha": ..., "tipo": "cliente"/"vendedor", "cashback": 0.0, "indicados": []}}

class Cliente:
    def __init__(self, nome, senha, tipo="cliente"):
        self.nome = nome
        self.senha = senha
        self.tipo = tipo
        self.cashback = 0.0
        self.indicados = []

    def indicar(self, novo_cliente):
        self.indicados.append(novo_cliente)

    def adicionar_cashback(self, valor):
        self.cashback += valor


def registrar_compra(indicado, valor):
    # Verifica quem indicou este cliente
    for usuario in usuarios.values():
        if indicado in usuario["indicados"]:
            cashback = valor * 0.10
            usuario["cashback"] += cashback


@app.route("/")
def index():
    if "usuario" in session:
        usuario = session["usuario"]
        return render_template("index.html", usuario=usuario, dados=usuarios)
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]
        if nome in usuarios and usuarios[nome]["senha"] == senha:
            session["usuario"] = nome
            return redirect(url_for("index"))
        return "Login inválido!"
    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]
        tipo = request.form["tipo"]  # cliente ou vendedor
        if nome not in usuarios:
            usuarios[nome] = {"senha": senha, "tipo": tipo, "cashback": 0.0, "indicados": []}
            return redirect(url_for("login"))
        return "Usuário já existe!"
    return render_template("cadastro.html")


@app.route("/registrar_compra", methods=["POST"])
def registrar():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]
    if usuarios[usuario]["tipo"] != "vendedor":
        return "Somente vendedores podem registrar compras!"

    indicado = request.form["indicado"]
    valor = float(request.form["valor"])

    if indicado not in usuarios:
        return "Cliente não encontrado!"

    registrar_compra(indicado, valor)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)