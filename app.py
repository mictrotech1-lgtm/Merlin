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
    
    # Primero buscamos en mictrotech.sab
    for clave, resp in conocimiento.items():
        if clave in m:
            return resp
    
    # Si no está en el .sab, usamos la lógica de Merlín
    respuesta = ""
    
    # Saludo inicial
    if "hola" in m and len(m) < 10:
        respuesta = "Saludos. Soy Merlín, el asistente de MICTROTECH. ¿Cómo te llamo? ⚡"
    
    # Nombre del usuario
    elif len(mensaje) > 2 and "?" not in mensaje:
        respuesta = f"Un gusto conocerte, {mensaje}. 👋\n\n¿En qué te ayudo hoy? Puedo contarte sobre nuestros planes, funcionalidades y tecnología BUFFER PRO."
    
    # Planes
    elif "plan" in m or "precio" in m:
        respuesta = """📋 NUESTROS PLANES:

🟢 **BÁSICO — $10.000 ARS / u$s 10**
- 1 sesión diaria
- 2 consultas BUFFER PRO
- Guardado de sesión

🔵 **PRO — $50.000 ARS / u$s 50**
- Sesiones ilimitadas
- Acceso total a BUFFER PRO
- Personalización completa
- Soporte prioritario

🏢 **EMPRESA — DEMO 7 DÍAS**
- Todo PRO + integración propia
- NDA y confidencialidad total

¿Cuál te interesa? 🤝"""
    
    # Buffer Pro
    elif "buffer" in m:
        respuesta = """⚡ **BUFFER PRO** — Nuestra tecnología

Es el sistema que procesa, filtra y da sentido a la información antes de responder. No es velocidad, es **sabiduría**:
- 🧠 Piensa antes de hablar
- 🛡️ Filtra ruido y detecta lo importante
- 💡 Responde con contexto y memoria

El corazón de Merlín. 🖤⚫"""
    
    # Despedida
    elif "chau" in m or "adiós" in m:
        respuesta = "Hasta luego. Estoy aquí cuando me necesites. 🛡️⚡"
    
    # Respuesta por defecto
    else:
        respuesta = f"Entendí: «{mensaje}»\n\n¿Querés saber sobre nuestros **planes**, la tecnología **BUFFER PRO**, o tenés una consulta específica? 🤔"
    
    return respuesta

# 🚀 RUTAS DEL SERVIDOR
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/static/<path:p>')
def recursos_estaticos(p):
    return send_from_directory(app.static_folder, p)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        texto = data.get("mensaje", "")
    except:
        return jsonify({"respuesta": "No entendí el mensaje 🤔"})
    
    respuesta = dar_respuesta(texto)
    return jsonify({"respuesta": respuesta})

# ⚙️ ARRANQUE FINAL
if __name__ == "__main__":
    print("✅ MERLÍN MICTROTECH ONLINE | CONECTADO A mictrotech.sab.txt")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
