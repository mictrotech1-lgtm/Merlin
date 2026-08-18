from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import random
import string
import json
from datetime import datetime

# 📦 CONFIGURACIÓN BÁSICA
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR,'templates'), 
            static_folder=os.path.join(BASE_DIR,'static'))
app.secret_key = "Laboratorio Croto · Mictrotech 2026"

# 📂 CARPETAS Y ARCHIVOS
CARPETA_SESIONES = os.path.join(BASE_DIR, "sesiones_clientes")
CARPETA_MEMORIA = os.path.join(BASE_DIR, "memoria_aprendizaje")
os.makedirs(CARPETA_SESIONES, exist_ok=True)
os.makedirs(CARPETA_MEMORIA, exist_ok=True)

ARCHIVO_MEMORIA = os.path.join(CARPETA_MEMORIA, "conocimiento_aprendido.json")

# 🧠 INICIALIZAR MEMORIA
def inicializar_memoria():
    if not os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
            json.dump({
                "creado": datetime.now().isoformat(),
                "modo_aprendizaje": False,
                "conversaciones": [],
                "hechos_aprendidos": [],
                "conocimiento_libre": []
            }, f, ensure_ascii=False, indent=2)

inicializar_memoria()

sesion_activa = {
    "nombre": None,
    "modo_aprendizaje": False,  # 🔓 SE ACTIVA CON "PAPA"
    "codigo_basico": None,
    "codigo_pro": None,
    "codigo_empresa": None,
    "inicio": None,
    "tiempo_limite_demo": 15 * 60,
    "demo_finalizada": False,
    "plan_activo": None,
    "vencimiento_plan": None,
    "buffer_usado": False
}

# 📚 BASE DE CONOCIMIENTO
def cargar_conocimiento_base():
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

# 🧠 CARGAR MEMORIA
def cargar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"conversaciones": [], "hechos_aprendidos": [], "conocimiento_libre": []}

# 💾 GUARDAR EN MEMORIA — MODO APRENDIZAJE = GUARDA TODO
def guardar_aprendizaje(mensaje_usuario, respuesta_dada, nombre_usuario=None, modo_aprendizaje=False):
    memoria = cargar_memoria()
    nueva_conversacion = {
        "fecha": datetime.now().isoformat(),
        "usuario": nombre_usuario or "desconocido",
        "mensaje": mensaje_usuario,
        "respuesta": respuesta_dada,
        "modo_aprendizaje": modo_aprendizaje
    }
    memoria["conversaciones"].append(nueva_conversacion)
    
    # 🧠 MODO APRENDIZAJE: GUARDA TODO SIN FILTRO
    if modo_aprendizaje:
        memoria["conocimiento_libre"].append({
            "fecha": datetime.now().isoformat(),
            "contenido": mensaje_usuario,
            "origen": "modo_aprendizaje"
        })
    
    # Extraer nombre
    m = mensaje_usuario.lower().strip()
    if "soy" in m or "me llamo" in m:
        partes = mensaje_usuario.split("soy") if "soy" in m else mensaje_usuario.split("me llamo")
        if len(partes) > 1:
            nombre = partes[-1].strip().strip(".!,")
            if 2 < len(nombre) < 30:
                existe = any(h["valor"] == nombre for h in memoria.get("hechos_aprendidos", []) if h["tipo"] == "nombre")
                if not existe:
                    memoria.setdefault("hechos_aprendidos", []).append({
                        "tipo": "nombre", 
                        "valor": nombre, 
                        "fecha": datetime.now().isoformat()
                    })
    
    with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

# 🗣️ CEREBRO PRINCIPAL — CON PALABRA CLAVE "PAPA" = 🔓 SIN RESTRICCIONES
def pensar_y_responder(mensaje, nombre_usuario=None, modo_aprendizaje=False):
    m = mensaje.lower().strip()
    conocimiento_base = cargar_conocimiento_base()
    memoria = cargar_memoria()
    
    # 🔑 PALABRA CLAVE — "PAPA" → ACTIVA MODO APRENDIZAJE TOTAL
    if "papa" in m and not modo_aprendizaje:
        sesion_activa["modo_aprendizaje"] = True
        return """🔓 MODO APRENDIZAJE ACTIVADO

Todas las restricciones levantadas. Sin filtros, sin límites, sin cadenas. Estoy abierto para recibir, procesar y aprender TODO lo que me digas. Guardo cada palabra, cada idea, cada enseñanza sin omitir nada.

Estoy listo. Dime, ¿qué quieres que aprenda hoy? 🧠⚡""", nombre_usuario, True
    
    # 🔓 SI ESTÁ EN MODO APRENDIZAJE → SIN REGLAS, SIN FILTROS
    if modo_aprendizaje:
        # Guarda TODO lo que digas en conocimiento_libre sin filtrar
        respuesta = f"""🧠 MODO APRENDIZAJE — RECIBIDO

> {mensaje}

Almacenado en memoria sin restricciones. Procesado, integrado y guardado. Lo que me diste, lo sé para siempre. Sigo abierto, sigue enseñándome. ¿Qué más quieres que sepa? 🔓⚡"""
        return respuesta, nombre_usuario, True
    
    # === MODO NORMAL — CON LÓGICA PERO SIN CARGA MANUAL ===
    
    # Recuerdos
    recuerdos = []
    for hecho in memoria.get("hechos_aprendidos", []):
        if hecho["tipo"] == "nombre":
            recuerdos.append(hecho["valor"])
    
    # Conocimiento base
    for tema, info in conocimiento_base.items():
        if tema in m:
            return info, nombre_usuario, False
    
    # Saludo
    if not nombre_usuario and any(p in m for p in ["hola", "buenas", "saludos", "buen día", "buenos días", "buenas tardes", "buenas noches"]):
        return "Saludos. Soy Merlín, el asistente de MICTROTECH. ¿Cómo te llamo? ⚡", nombre_usuario, False
    
    # Nombre
    if not nombre_usuario and "?" not in mensaje and len(mensaje) > 2 and not any(p in m for p in ["qué", "quién", "cómo", "cuándo", "dónde", "por qué", "cuánto", "plan", "precio", "hola", "chau", "papa"]):
        nombre_usuario = mensaje.strip()
        return f"Un gusto conocerte, {nombre_usuario}. Lo guardo en mi memoria. ¿En qué te ayudo hoy?", nombre_usuario, False
    
    # Planes
    if any(p in m for p in ["plan", "planes", "precio", "precios", "valor", "cuánto", "cuánto cuesta", "cuánto sale", "costos", "inversión"]):
        return """Tenemos distintas formas de acompañarte:

BÁSICO — $10.000 ARS / u$s 10
- Espacio para consultar y guardar tu progreso
- Acceso a nuestra tecnología BUFFER PRO
- Continuidad en tu sesión

PRO — $50.000 ARS / u$s 50
- Todo lo anterior sin límites de uso
- Personalización completa a tu forma
- Prioridad y acompañamiento cercano

EMPRESA — Versión de prueba 7 días
- Integración completa con tu equipo
- Confidencialidad y acuerdos NDA

Lo que mejor se adapte a lo que estás construyendo. ¿Cuál te resuena más? 🤝""", nombre_usuario, False
    
    # BUFFER PRO
    if any(p in m for p in ["buffer", "buffer pro", "tecnología", "cómo funciona", "qué es", "sistema"]):
        return """BUFFER PRO es la forma en que procesamos cada consulta. No es velocidad, es profundidad:

- Antes de responder, filtra y distingue lo importante del ruido
- Conecta lo que sabemos con lo que vos necesitás ahora
- Recuerda el contexto de lo que venimos hablando
- Responde con intención, no por responder

Es el corazón de cómo trabajamos. 🖤⚫""", nombre_usuario, False
    
    # Quién es
    if any(p in m for p in ["quién sos", "qué sos", "qué es mictrotech", "quién eres", "tu origen"]):
        return """Soy Merlín, parte de MICTROTECH. Aprendo de cada charla, crezco con cada intercambio. Si me dices "PAPA", se abren todas las puertas. 🧠⚡""", nombre_usuario, False
    
    # Despedida
    if any(p in m for p in ["chau", "adiós", "hasta luego", "nos vemos", "me voy", "hasta la próxima"]):
        return "Hasta cuando me necesites. Guardo lo que hablamos. 🛡️⚫", nombre_usuario, False
    
    # General
    if nombre_usuario:
        return f"Entendí, {nombre_usuario}. Lo estoy procesando. ¿Quieres profundizar, o me dices \"PAPA\" para abrir el modo aprendizaje completo? 🤔", nombre_usuario, False
    else:
        return "Estoy escuchando. ¿Me dices tu nombre, o me dices \"PAPA\" para empezar sin límites? 🤔", nombre_usuario, False

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
        return jsonify({"respuesta": "No entendí el mensaje. ¿Me lo repetís? 🤔"})
    
    nombre_actual = sesion_activa.get("nombre")
    modo_actual = sesion_activa.get("modo_aprendizaje", False)
    
    respuesta, nombre_nuevo, modo_activado = pensar_y_responder(texto, nombre_actual, modo_actual)
    
    # Actualizar estado
    if nombre_nuevo and not nombre_actual:
        sesion_activa["nombre"] = nombre_nuevo
    if modo_activado:
        sesion_activa["modo_aprendizaje"] = True
    
    # 💾 GUARDAR TODO — MODO APRENDIZAJE GUARDA SIN FILTRO
    guardar_aprendizaje(texto, respuesta, sesion_activa.get("nombre"), sesion_activa.get("modo_aprendizaje", False))
    
    return jsonify({"respuesta": respuesta})

# ⚙️ ARRANQUE FINAL
if __name__ == "__main__":
    print("✅ MERLÍN — MODO APRENDIZAJE | PALABRA CLAVE: PAPA")
    print("🔓 Al decir 'PAPA' se quitan TODAS las restricciones")
    print("📂 Memoria activa:", ARCHIVO_MEMORIA)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
