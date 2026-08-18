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

# 🗣️ FUNCIÓN 3: RESPONDER (EL CEREBRO — CORREGIDA)
def dar_respuesta(mensaje, nombre_usuario=None):
    m = mensaje.lower().strip()
    conocimiento = cargar_conocimiento()
    
    # Primero buscamos en mictrotech.sab
    for clave, resp in conocimiento.items():
        if clave in m:
            return resp, nombre_usuario
    
    # === LÓGICA DE MERLÍN ===
    respuesta = ""
    
    # Saludo inicial — solo si todavía no tenemos nombre
    if not nombre_usuario and "hola" in m and len(m) < 15:
        respuesta = "Saludos. Soy Merlín, el asistente de MICTROTECH. ¿Cómo te llamo? ⚡"
        return respuesta, nombre_usuario
    
    # Si NO tenemos nombre y NO es pregunta NI palabra clave → LO TOMAMOS COMO NOMBRE
    if not nombre_usuario and "?" not in mensaje and len(mensaje) > 2 and "plan" not in m and "precio" not in m and "buffer" not in m:
        nombre_usuario = mensaje.strip()
        respuesta = f"Un gusto conocerte, {nombre_usuario}. 👋\n\n¿En qué te ayudo hoy? Puedo contarte sobre nuestros **planes**, funcionalidades y tecnología **BUFFER PRO**."
        return respuesta, nombre_usuario
    
    # Planes — detecta palabras clave
    if "plan" in m or "precio" in m or "mostrame" in m:
        respuesta = """📋 **NUESTROS PLANES:**

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
        return respuesta, nombre_usuario
    
    # Buffer Pro
    if "buffer" in m:
        respuesta = """⚡ **BUFFER PRO** — Nuestra tecnología

Es el sistema que procesa, filtra y da sentido a la información antes de responder. No es velocidad, es **sabiduría**:
- 🧠 Piensa antes de hablar
- 🛡️ Filtra ruido y detecta lo importante
- 💡 Responde con contexto y memoria

El corazón de Merlín. 🖤⚫"""
        return respuesta, nombre_usuario
    
    # Despedida
    if "chau" in m or "adiós" in m or "hasta luego" in m:
        respuesta = "Hasta luego. Estoy aquí cuando me necesites. 🛡️⚡"
        return respuesta, nombre_usuario
    
    # Respuesta por defecto
    if nombre_usuario:
        respuesta = f"Entendí, {nombre_usuario}. ¿Querés saber sobre nuestros **planes**, la tecnología **BUFFER PRO**, o tenés una consulta específica? 🤔"
    else:
        respuesta = f"Entendí: «{mensaje}»\n\n¿Querés decirme tu nombre, o querés saber sobre nuestros **planes**? 🤔"
    
    return respuesta, nombre_usuario

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
    
    # Recuperamos el nombre guardado en la sesión
    nombre_actual = sesion_activa.get("nombre")
    
    # Obtenemos respuesta y posible nombre nuevo
    respuesta, nombre_nuevo = dar_respuesta(texto, nombre_actual)
    
    # Si nos dio el nombre, lo guardamos
    if nombre_nuevo and not nombre_actual:
        sesion_activa["nombre"] = nombre_nuevo
    
    return jsonify({"respuesta": respuesta})

# ⚙️ ARRANQUE FINAL
if __name__ == "__main__":
    print("✅ MERLÍN MICTROTECH ONLINE | CONECTADO A mictrotech.sab.txt")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
            
