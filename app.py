from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import random
import string
import time

# 📦 CONFIGURACIÓN BÁSICA
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR,'templates'), 
            static_folder=os.path.join(BASE_DIR,'static'))
app.secret_key = "Laboratorio Croto · Mictrotech 2026"

# 📂 CARPETAS Y ESTADO
CARPETA_SESIONES = os.path.join(BASE_DIR, "sesiones_clientes")
os.makedirs(CARPETA_SESIONES, exist_ok=True)

sesion_activa = {
    "nombre": None,
    "codigo_basico": None,
    "codigo_pro": None,
    "codigo_empresa": None,
    "inicio": None,
    "tiempo_limite_demo": 15 * 60,
    "demo_finalizada": False,
    "plan_activo": None,
    "vencimiento_plan": None,
    "buffer_usado": 0
}

# 🧠 FUNCIÓN 1: CARGAR NUESTRO CONOCIMIENTO
def cargar_conocimiento():
    sab_path = os.path.join(BASE_DIR, "mictrotech.sab")
    conocimiento = {}
    if os.path.exists(sab_path):
        with open(sab_path, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if "=" in linea and not linea.startswith(("=", "-", "#")):
                    clave, valor = linea.split("=", 1)
                    conocimiento[clave.strip().lower()] = valor.strip()
    return conocimiento

# 🎫 FUNCIÓN 2: GENERAR CÓDIGOS
def generar_codigos():
    return {
        "basico": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
        "pro": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
        "empresa": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    }

# 🗣️ FUNCIÓN 3: RESPONDER (EL CEREBRO)
def dar_respuesta(mensaje):
    m = mensaje.lower().strip()
    conocimiento = cargar_conocimiento()
    for clave, resp in conocimiento.items():
        if clave in m:
            return resp
    return "🧙‍♂️ Estoy procesando tu consulta con nuestra tecnología BUFFER PRO..."

# 🚀 RUTAS DEL SERVIDOR
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/static/<path:p>')
def recursos_estaticos(p):
    return send_from_directory(app.static_folder, p)

@app.route("/chat", methods=["POST"])
def chat():
    texto = request.json.get("mensaje", "")
    respuesta = dar_respuesta(texto)
    return jsonify({"respuesta": respuesta})

# ⚙️ ARRANQUE FINAL
if __name__ == "__main__":
    print("✅ MERLÍN MICTROTECH ONLINE | CONECTADO A mictrotech.sab.txt")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
