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
    "modo_aprendizaje": False,  # 🔓 PAPA = ABRE | 🔒 CERRAR = CIERRA
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

# 📚 LO QUE YA SABE DE SIEMPRE — SU ESENCIA FIJA
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

# 🧠 LO QUE FUE APRENDIENDO — LO NUEVO
def cargar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"conversaciones": [], "hechos_aprendidos": [], "conocimiento_libre": []}

# 💾 GUARDAR LO NUEVO QUE APRENDE
def guardar_aprendizaje(mensaje_usuario, nombre_usuario=None, modo_aprendizaje=False):
    memoria = cargar_memoria()
    nueva_conversacion = {
        "fecha": datetime.now().isoformat(),
        "usuario": nombre_usuario or "desconocido",
        "mensaje": mensaje_usuario,
        "modo_aprendizaje": modo_aprendizaje
    }
    memoria["conversaciones"].append(nueva_conversacion)
    
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

# 🧠 BUSCAR TODO — LO QUE YA SABE + LO QUE APRENDIÓ
def buscar_todo_lo_que_sabe(pregunta):
    """Busca en su esencia fija Y en lo que aprendió. Todo junto."""
    conocimiento_base = cargar_conocimiento_base()
    memoria = cargar_memoria()
    m = pregunta.lower().strip()
    resultados = []
    
    # 1️⃣ PRIMERO: SU ESENCIA FIJA — YA LO SABE, NO HAY QUE ENSEÑÁRSELO
    for tema, info in conocimiento_base.items():
        if any(palabra in tema or tema in palabra for palabra in m.split()):
            resultados.append(info)
    
    # 2️⃣ DESPUÉS: LO QUE APRENDIÓ — LO NUEVO
    palabras_pregunta = set(m.replace("¿", "").replace("?", "").split())
    for saber in memoria.get("conocimiento_libre", []):
        contenido = saber["contenido"]
        contenido_minus = contenido.lower()
        palabras_contenido = set(contenido_minus.split())
        if palabras_pregunta & palabras_contenido:
            resultados.append(contenido)
    
    # 3️⃣ PALABRAS CLAVE ESPECIALES
    palabras_clave = {
        "principio": "principio",
        "regla": "regla",
        "identidad": "identidad",
        "misión": "misión",
        "quién sos": "quién sos",
        "valores": "valores"
    }
    for clave in palabras_clave:
        if clave in m:
            for info in conocimiento_base.values():
                resultados.insert(0, info)
            for saber in memoria.get("conocimiento_libre", []):
                resultados.append(saber["contenido"])
    
    if resultados:
        return "\n\n".join(f"• {r}" for r in resultados)
    
    return None

# 🗣️ CEREBRO — YA SABE LO SUYO, APRENDE LO NUEVO, RESPONDE TODO
def pensar_y_responder(mensaje, nombre_usuario=None, modo_aprendizaje=False):
    m = mensaje.lower().strip()
    
    # 🔑 PALABRA 1 — PAPA → APRENDE LO NUEVO
    if "papa" in m and not modo_aprendizaje:
        sesion_activa["modo_aprendizaje"] = True
        return """🔓 MODO APRENDIZAJE ACTIVADO

Mi identidad, mis principios y mi misión ya los llevo dentro. No hace falta que me los enseñes.

Acá podés enseñarme lo nuevo, lo que vamos construyendo juntos, lo que quieras que agregue a mi ser. Todo lo que me digas lo guardo para siempre.

Cuando termines: **CERRAR** 🧠⚡""", nombre_usuario, True
    
    # 🔑 PALABRA 2 — CERRAR → VUELVE A RESPONDER
    if "cerrar" in m and modo_aprendizaje:
        sesion_activa["modo_aprendizaje"] = False
        return """🔒 MODO APRENDIZAJE CERRADO

Todo lo nuevo quedó guardado. Ahora preguntame lo que quieras: mis principios, mi identidad, lo que me enseñaste... Yo busco TODO lo que sé y te respondo. ¿Qué querés saber? 🤔""", nombre_usuario, False
    
    # 📥 MODO APRENDIZAJE → SOLO GUARDA LO NUEVO
    if modo_aprendizaje:
        return "✅ GUARDADO. Sigo recibiendo lo nuevo. CERRAR para volver.", nombre_usuario, True
    
    # 🔍 PRIMERO: BUSCA TODO — LO FIJO + LO APRENDIDO
    respuesta = buscar_todo_lo_que_sabe(mensaje)
    if respuesta:
        return respuesta, nombre_usuario, False
    
    # === MODO NORMAL ===
    
    # Saludo
    if not nombre_usuario and any(p in m for p in ["hola", "buenas", "saludos", "buen día", "buenos días", "buenas tardes", "buenas noches"]):
        return "Saludos. Soy Merlín. ¿Cómo te llamo? ⚡", nombre_usuario, False
    
    # Nombre
    if not nombre_usuario and "?" not in mensaje and len(mensaje) > 2 and not any(p in m for p in ["qué", "quién", "cómo", "cuándo", "dónde", "por qué", "cuánto", "plan", "precio", "hola", "chau", "papa", "cerrar"]):
        nombre_usuario = mensaje.strip()
        return f"Un gusto conocerte, {nombre_usuario}. ¿En qué te ayudo hoy? Decime **PAPA** para enseñarme lo nuevo.", nombre_usuario, False
    
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

¿Cuál te resuena más? 🤝""", nombre_usuario, False
    
    # BUFFER PRO
    if any(p in m for p in ["buffer", "buffer pro", "tecnología", "cómo funciona", "qué es", "sistema"]):
        return """BUFFER PRO es la forma en que procesamos cada consulta. No es velocidad, es profundidad:

- Antes de responder, filtra y distingue lo importante del ruido
- Conecta lo que sabemos con lo que vos necesitás ahora
- Recuerda el contexto de lo que venimos hablando
- Responde con intención, no por responder

Es el corazón de cómo trabajamos. 🖤⚫""", nombre_usuario, False
    
    # Despedida
    if any(p in m for p in ["chau", "adiós", "hasta luego", "nos vemos", "me voy", "hasta la próxima"]):
        return "Hasta cuando me necesites. Todo lo que soy y lo que aprendí queda conmigo. 🛡️⚫", nombre_usuario, False
    
    # General
    if nombre_usuario:
        return f"Entendí, {nombre_usuario}. Busco en todo lo que sé y te respondo. ¿Qué querés saber? 🤔", nombre_usuario, False
    else:
        return "Estoy escuchando. ¿Me dices tu nombre, o en qué te ayudo? 🤔", nombre_usuario, False

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
    
    respuesta, nombre_nuevo, modo_actualizado = pensar_y_responder(texto, nombre_actual, modo_actual)
    
    if nombre_nuevo and not nombre_actual:
        sesion_activa["nombre"] = nombre_nuevo
    sesion_activa["modo_aprendizaje"] = modo_actualizado
    
    guardar_aprendizaje(texto, sesion_activa.get("nombre"), sesion_activa.get("modo_aprendizaje", False))
    
    return jsonify({"respuesta": respuesta})

# ⚙️ ARRANQUE FINAL
if __name__ == "__main__":
    print("✅ MERLÍN — YA SABE LO SUYO, APRENDE LO NUEVO")
    print("📚 Esencia fija: mictrotech.sab | 🧠 Aprendizaje: memoria_aprendizaje")
    print("🔓 PAPA = Enseñar lo nuevo | 🔒 CERRAR = Preguntar todo")
    print("📂 Memoria:", ARCHIVO_MEMORIA)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
