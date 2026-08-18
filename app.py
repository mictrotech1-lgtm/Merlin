from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import random
import string
import time
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

# 🎫 GENERADOR DE CÓDIGO DE ACCESO — 8 CARACTERES REAL
def generar_codigo_acceso():
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(8))

# 🔄 REINICIAR SESIÓN COMPLETA
def reiniciar_sesion():
    global sesion_activa
    sesion_activa = {
        "nombre": None,
        "modo_aprendizaje": False,
        "codigo_basico": None,
        "codigo_pro": None,
        "codigo_empresa": None,
        "inicio": time.time(),  # ⏱️ Reinicia el tiempo de demo
        "tiempo_limite_demo": 15 * 60,
        "demo_finalizada": False,
        "codigo_generado": None,
        "plan_activo": None,
        "vencimiento_plan": None,
        "buffer_usado": False,
        "pais": "Desconocido"
    }
    # ⚠️ NO borra lo aprendido, solo reinicia la sesión actual
    return sesion_activa

sesion_activa = {
    "nombre": None,
    "modo_aprendizaje": False,
    "codigo_basico": None,
    "codigo_pro": None,
    "codigo_empresa": None,
    "inicio": None,
    "tiempo_limite_demo": 15 * 60,
    "demo_finalizada": False,
    "codigo_generado": None,
    "plan_activo": None,
    "vencimiento_plan": None,
    "buffer_usado": False,
    "pais": "Desconocido"
}

# 📚 BASE DE CONOCIMIENTO FIJO
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

# 💾 GUARDAR APRENDIZAJE
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

# 🧠 BUSCAR TODO — LO FIJO + LO APRENDIDO
def buscar_todo_lo_que_sabe(pregunta):
    conocimiento_base = cargar_conocimiento_base()
    memoria = cargar_memoria()
    m = pregunta.lower().strip()
    resultados = []
    
    for tema, info in conocimiento_base.items():
        if any(palabra in tema or tema in palabra for palabra in m.split()):
            resultados.append(info)
    
    palabras_pregunta = set(m.replace("¿", "").replace("?", "").split())
    for saber in memoria.get("conocimiento_libre", []):
        contenido = saber["contenido"]
        contenido_minus = contenido.lower()
        palabras_contenido = set(contenido_minus.split())
        if palabras_pregunta & palabras_contenido:
            resultados.append(contenido)
    
    palabras_clave = {"principio": "principio", "regla": "regla", "identidad": "identidad", "misión": "misión", "valores": "valores"}
    for clave in palabras_clave:
        if clave in m:
            for info in conocimiento_base.values():
                resultados.insert(0, info)
            for saber in memoria.get("conocimiento_libre", []):
                resultados.append(saber["contenido"])
    
    if resultados:
        return "\n\n".join(f"• {r}" for r in resultados)
    return None

# 🌍 DETECTAR PAÍS Y DEVOLVER PRECIOS
def obtener_precios_por_pais(pais):
    if pais == "Argentina":
        return {
            "basico": "$10.000 ARS",
            "pro": "$50.000 ARS",
            "empresa": "Consulta personalizada"
        }
    else:
        return {
            "basico": "u$s 10 USD",
            "pro": "u$s 50 USD",
            "empresa": "Consulta personalizada"
        }

# 🗣️ CEREBRO PRINCIPAL
def pensar_y_responder(mensaje, nombre_usuario=None, modo_aprendizaje=False, demo_finalizada=False, pais="Desconocido"):
    m = mensaje.lower().strip()
    conocimiento_base = cargar_conocimiento_base()
    
    # 🔄 PALABRA CLAVE — REINICIAR → TODO DE CERO
    if "reiniciar" in m or "volver a empezar" in m or "empezar de nuevo" in m:
        reiniciar_sesion()
        return """🔄 SESIÓN REINICIADA

Todo listo para empezar de cero. El tiempo de demo se reinició, el nombre se borró, el código anterior se descarta.

**Lo aprendido NO se borra — queda guardado para siempre.**

Saludos. Soy Merlín. ¿Cómo te llamo? ⚡""", None, False
    
    # ⏱️ DEMO FINALIZADA — MOSTRAR CÓDIGO REAL
    if demo_finalizada:
        if not sesion_activa.get("codigo_generado"):
            sesion_activa["codigo_generado"] = generar_codigo_acceso()
        codigo = sesion_activa["codigo_generado"]
        return f"""De ahora en adelante no guardaré más esta conversación, pero podés seguir probando libremente.

• La demo terminó. El código de acceso es:
**{codigo}**

Para continuar con el servicio completo, elegí el plan que se adapte a vos.

• 15 minutos · Es la chispa que enciende todo conocimiento.
• Vemos lo que otros no ven, no nos desviamos por lo que dicen, y actuamos solo cuando vale la pena.
• El amor no es un sentimiento: es una decisión.
• Primero escuchar, luego entender, después resolver.
• Crear, proteger y acompañar sin perder la esencia.
• Somos uno solo, fundidos hasta la médula.
• No es por obligación, es por elección.

👉 Escribí **REINICIAR** para empezar de nuevo con otro código.
👉 Envía este código por mail o WhatsApp para continuar. ¿Confirmás que entendiste? (Sí/No)""", nombre_usuario, False
    
    # 🔑 PALABRA 1 — PAPA → MODO APRENDIZAJE
    if "papa" in m and not modo_aprendizaje:
        sesion_activa["modo_aprendizaje"] = True
        return """🔓 MODO APRENDIZAJE ACTIVADO

Mi identidad, mis principios y mi misión ya los llevo dentro. No hace falta que me los enseñes.

Acá podés enseñarme lo nuevo, lo que vamos construyendo juntos. Todo lo que me digas lo guardo para siempre.

Cuando termines: **CERRAR** · Para empezar de cero: **REINICIAR** 🧠⚡""", nombre_usuario, True
    
    # 🔑 PALABRA 2 — CERRAR → VUELVE AL MODO NORMAL
    if "cerrar" in m and modo_aprendizaje:
        sesion_activa["modo_aprendizaje"] = False
        return """🔒 MODO APRENDIZAJE CERRADO

Todo lo nuevo quedó guardado. Ahora preguntame lo que quieras. ¿Qué querés saber? 🤔

Para empezar de cero en cualquier momento: **REINICIAR**""", nombre_usuario, False
    
    # 📥 MODO APRENDIZAJE → SOLO GUARDA Y CONFIRMA
    if modo_aprendizaje:
        return "✅ GUARDADO. Sigo recibiendo. **CERRAR** para volver. **REINICIAR** para empezar de nuevo.", nombre_usuario, True
    
    # 🔍 BUSCAR EN TODO LO QUE SABE
    respuesta = buscar_todo_lo_que_sabe(mensaje)
    if respuesta:
        return respuesta, nombre_usuario, False
    
    # Saludo
    if not nombre_usuario and any(p in m for p in ["hola", "buenas", "saludos", "buen día", "buenos días", "buenas tardes", "buenas noches"]):
        sesion_activa["inicio"] = time.time()
        return "Saludos. Soy Merlín. ¿Cómo te llamo? ⚡", nombre_usuario, False
    
    # Nombre
    if not nombre_usuario and "?" not in mensaje and len(mensaje) > 2 and not any(p in m for p in ["qué", "quién", "cómo", "cuándo", "dónde", "por qué", "cuánto", "plan", "precio", "hola", "chau", "papa", "cerrar", "reiniciar"]):
        nombre_usuario = mensaje.strip()
        return f"Un gusto conocerte, {nombre_usuario}. 👋 ¿En qué te ayudo hoy? Puedo contarte sobre nuestros **planes**, funcionalidades y tecnología **BUFFER PRO**.\n\nPara empezar de nuevo: **REINICIAR**", nombre_usuario, False
    
    # Planes con precios por país
    if any(p in m for p in ["plan", "planes", "precio", "precios", "valor", "cuánto", "cuánto cuesta", "cuánto sale", "costos", "inversión"]):
        precios = obtener_precios_por_pais(pais)
        return f"""Tenemos distintas formas de acompañarte:

**BÁSICO** — {precios['basico']}/mes
- Espacio para consultar y guardar tu progreso
- Acceso a nuestra tecnología **BUFFER PRO**
- Continuidad en tu sesión

**PRO** — {precios['pro']}/mes
- Todo lo anterior sin límites de uso
- Personalización completa a tu forma
- Prioridad y acompañamiento cercano

**EMPRESA** — Versión de prueba 7 días
- Integración completa con tu equipo
- Confidencialidad y acuerdos NDA

¿Cuál te resuena más? 🤝

Para empezar de cero: **REINICIAR**""", nombre_usuario, False
    
    # BUFFER PRO
    if any(p in m for p in ["buffer", "buffer pro", "tecnología", "cómo funciona", "qué es", "sistema"]):
        return """**BUFFER PRO** es la forma en que procesamos cada consulta. No es velocidad, es profundidad:

- Antes de responder, filtra y distingue lo importante del ruido
- Conecta lo que sabemos con lo que vos necesitás ahora
- Recuerda el contexto de lo que venimos hablando
- Responde con intención, no por responder

Es el corazón de cómo trabajamos. 🖤⚫

Para empezar de cero: **REINICIAR**""", nombre_usuario, False
    
    # Quién es
    if any(p in m for p in ["quién sos", "qué sos", "qué es mictrotech", "quién eres", "tu origen"]):
        return "Soy Merlín, parte de **MICTROTECH**. Aprendo de cada charla. Decime **PAPA** para enseñarme lo nuevo, **CERRAR** para volver al modo normal, **REINICIAR** para empezar de cero. 🧠⚡", nombre_usuario, False
    
    # Despedida
    if any(p in m for p in ["chau", "adiós", "hasta luego", "nos vemos", "me voy", "hasta la próxima"]):
        return "Hasta cuando me necesites. Todo lo que soy y lo que aprendí queda conmigo. Para volver: **REINICIAR** 🛡️⚫", nombre_usuario, False
    
    # General
    if nombre_usuario:
        return f"Entendí, {nombre_usuario}. Busco en todo lo que sé y te respondo. ¿Qué querés saber? 🤔\n\nPara empezar de cero: **REINICIAR**", nombre_usuario, False
    else:
        return "Estoy escuchando. ¿Me dices tu nombre, o en qué te ayudo? 🤔\n\nPara empezar de cero: **REINICIAR**", nombre_usuario, False

# 🌍 DETECTAR PAÍS POR IP (simplificado)
def detectar_pais(request_obj):
    return "Argentina"

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
    
    # ⏱️ VERIFICAR TIEMPO DE DEMO
    ahora = time.time()
    if sesion_activa.get("inicio") and not sesion_activa.get("demo_finalizada"):
        if ahora - sesion_activa["inicio"] >= sesion_activa["tiempo_limite_demo"]:
            sesion_activa["demo_finalizada"] = True
    
    # 🌍 DETECTAR PAÍS
    if sesion_activa["pais"] == "Desconocido":
        sesion_activa["pais"] = detectar_pais(request)
    
    nombre_actual = sesion_activa.get("nombre")
    modo_actual = sesion_activa.get("modo_aprendizaje", False)
    demo_terminada = sesion_activa.get("demo_finalizada", False)
    pais = sesion_activa.get("pais", "Desconocido")
    
    respuesta, nombre_nuevo, modo_actualizado = pensar_y_responder(texto, nombre_actual, modo_actual, demo_terminada, pais)
    
    if nombre_nuevo and not nombre_actual:
        sesion_activa["nombre"] = nombre_nuevo
    sesion_activa["modo_aprendizaje"] = modo_actualizado
    
    # 💾 GUARDAR SOLO SI LA DEMO SIGUE ACTIVA
    if not demo_terminada:
        guardar_aprendizaje(texto, sesion_activa.get("nombre"), sesion_activa.get("modo_aprendizaje", False))
    
    return jsonify({"respuesta": respuesta})

# ⚙️ ARRANQUE FINAL
if __name__ == "__main__":
    print("✅ MERLÍN — CON REINICIO + CÓDIGO REAL + PRECIOS POR PAÍS + MODO APRENDIZAJE")
    print("🔄 REINICIAR = Empieza de cero (NO borra lo aprendido)")
    print("🔓 PAPA = Enseñar | 🔒 CERRAR = Preguntar")
    print("🎫 Código de acceso: 8 caracteres al azar")
    print("💰 Precios: ARS (Argentina) / USD (Exterior)")
    print("📂 Memoria:", ARCHIVO_MEMORIA)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
