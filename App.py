from flask import Flask, render_template, send_from_directory, request, jsonify, session
import os
import random
import string
import time
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR,'templates'), static_folder=os.path.join(BASE_DIR,'static'))
app.secret_key = "Laboratorio Croto · Mictrotech 2026"

CARPETA_SESIONES = os.path.join(BASE_DIR, "sesiones_clientes")
os.makedirs(CARPETA_SESIONES, exist_ok=True)

sesion_activa = {
    "nombre": None, "codigo_basico": None, "codigo_pro": None, "codigo_empresa": None,
    "inicio": None, "tiempo_limite_demo": 15 * 60, "tiempo_limite_basico_pro": 30 * 24 * 60 * 60,
    "tiempo_limite_empresa": 7 * 24 * 60 * 60, "demo_finalizada": False, "plan_activo": None, 
    "vencimiento_plan": None, "buffer_usado": 0
}

@app.before_request
def limpiar_sesion_vieja():
    if not session.get("nueva_conexion"):
        session.clear()
        sesion_activa.update({
            "nombre": None, "codigo_basico": None, "codigo_pro": None, "codigo_empresa": None,
            "inicio": None, "demo_finalizada": False, "plan_activo": None, 
            "vencimiento_plan": None, "buffer_usado": 0
        })
        session["nueva_conexion"] = True

def obtener_pais_cliente():
    try:
        ip = request.remote_addr
        if ip in ["127.0.0.1", "::1"]: return "Local"
        respuesta = requests.get(f"https://ipapi.co/{ip}/country_name/", timeout=3)
        return respuesta.text.strip() if respuesta.status_code == 200 else "No identificado"
    except: return "No identificado"

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

def generar_codigos():
    return {
        "basico": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
        "pro": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
        "empresa": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    }

def respuesta_interna(mensaje):
    m = mensaje.lower().strip()
    conocimiento = cargar_conocimiento()
    for clave, resp in conocimiento.items():
        if clave in m: return resp

    tiene_acceso = sesion_activa["plan_activo"] in ["PRO", "EMPRESA"]
    puede_probar = sesion_activa["plan_activo"] is None and sesion_activa["buffer_usado"] < 2

    if not tiene_acceso and not puede_probar:
        return """🧙‍♂️ Esta función es de **PLAN PRO / EMPRESA** 💎
Ya usaste tus 2 consultas BUFFER PRO gratis.
Activá tu plan con un código para seguir."""

    aviso = ""
    if puede_probar:
        sesion_activa["buffer_usado"] += 1
        restantes = 2 - sesion_activa["buffer_usado"]
        if restantes > 0: aviso = f"\n\n⚡ Te quedan **{restantes} consultas BUFFER PRO** gratis"

    return f"""🧙‍♂️ <span style="background:#00D4FF; color:#000; font-weight:bold; padding:3px 8px; border-radius:6px;">BUFFER PRO ACTIVADO</span>{aviso}

Consulté nuestra base sellada y esto es lo que encontré:
> Respuesta generada por Merlín Mictrotech"""

def manejar_sesion(texto):
    t = texto.lower().strip()
    
    if "planes" in t:
        pais = obtener_pais_cliente()
        if "Argentina" in pais:
            return """🧙‍♂️ 💎 **PLANES MICTROTECH**

| FUNCIONALIDAD | BÁSICO | PRO / EMPRESA |
| --- | --- | --- |
| Base de conocimiento propia | ✅ | ✅ |
| Soporte WhatsApp | ✅ | ✅ |
| Búsqueda externa + BUFFER PRO | ❌ | ✅ |

🔹 **BÁSICO** - 30 días → **$ 10.000 ARS**
🔹 **PRO** - 30 días + BUFFER PRO → **$ 50.000 ARS**
🔹 **EMPRESA** - 7 días Demo Total → **A consultar**

Decime cuál querés activar."""
        else:
            return """🧙‍♂️ 💎 **OUR PLANS**
BASIC: USD 10 / 30 days
PRO: USD 50 / 30 days + BUFFER PRO
COMPANY DEMO: On request"""

    if sesion_activa["plan_activo"] and sesion_activa["vencimiento_plan"]:
        if time.time() > sesion_activa["vencimiento_plan"]:
            sesion_activa["plan_activo"] = None
            sesion_activa["demo_finalizada"] = True
            return "🧙‍♂️ ⏳ **PERÍODO FINALIZADO**\nTu acceso venció. Escribe **PLANES** para renovar."

    if sesion_activa["demo_finalizada"]:
        if sesion_activa["codigo_basico"] and sesion_activa["codigo_basico"].lower() in t:
            sesion_activa.update({"demo_finalizada": False, "plan_activo": "BASICO", "vencimiento_plan": time.time() + sesion_activa["tiempo_limite_basico_pro"]})
            return "🧙‍♂️ ✅ **CÓDIGO BÁSICO VALIDADO**\nActivado por 30 días."
        elif sesion_activa["codigo_pro"] and sesion_activa["codigo_pro"].lower() in t:
            sesion_activa.update({"demo_finalizada": False, "plan_activo": "PRO", "vencimiento_plan": time.time() + sesion_activa["tiempo_limite_basico_pro"]})
            return "🧙‍♂️ ✅ **CÓDIGO PRO VALIDADO**\nActivado por 30 días + BUFFER PRO."
        elif sesion_activa["codigo_empresa"] and sesion_activa["codigo_empresa"].lower() in t:
            sesion_activa.update({"demo_finalizada": False, "plan_activo": "EMPRESA", "vencimiento_plan": time.time() + sesion_activa["tiempo_limite_empresa"]})
            return "🧙‍♂️ ✅ **DEMO EMPRESARIAL ACTIVADA**\nAcceso total por 7 días."
        else: return "🧙‍♂️ Escribe tu código de activación o **PLANES**"

    if sesion_activa["inicio"] and time.time() - sesion_activa["inicio"] > sesion_activa["tiempo_limite_demo"]:
        sesion_activa["demo_finalizada"] = True
        return f"""🧙‍♂️ ⏳ **PRUEBA FINALIZADA**

Tus códigos de activación:
• BÁSICO: **{sesion_activa['codigo_basico']}**
• PRO: **{sesion_activa['codigo_pro']}**
• EMPRESA: **{sesion_activa['codigo_empresa']}**

Escribe el código para activar o **PLANES**."""

    if not sesion_activa["nombre"]:
        if len(t) > 1:
            nombre = texto.strip().title()
            codigos = generar_codigos()
            sesion_activa.update({
                "nombre": nombre, "codigo_basico": codigos["basico"], "codigo_pro": codigos["pro"], 
                "codigo_empresa": codigos["empresa"], "inicio": time.time()
            })
            pais = obtener_pais_cliente()
            ruta = os.path.join(CARPETA_SESIONES, f"{nombre}.txt")
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(f"=== SESIÓN - {nombre} ===\nPAÍS: {pais}\nBÁSICO: {codigos['basico']}\nPRO: {codigos['pro']}\nEMPRESA: {codigos['empresa']}\n\n")
            
            return f"""🧙‍♂️ Un gusto **{nombre}** 🗺️ **{pais}**

🔑 Tus códigos de activación:
• BÁSICO: **{codigos['basico']}**
• PRO: **{codigos['pro']}**
• EMPRESA: **{codigos['empresa']}**

Tenés **2 consultas BUFFER PRO GRATIS**. ¿En qué te ayudo?"""
        else: return "🧙‍♂️ Para comenzar, ¿cómo te llamo?"
    
    elif "empezar de nuevo" in t or "reiniciar" in t:
        codigos = generar_codigos()
        sesion_activa.update({
            "codigo_basico": codigos["basico"], "codigo_pro": codigos["pro"], "codigo_empresa": codigos["empresa"],
            "inicio": time.time(), "demo_finalizada": False, "plan_activo": None, "vencimiento_plan": None, "buffer_usado": 0
        })
        return "🧙‍♂️ Reiniciado. Nuevos códigos y 2 consultas gratis listos."
    
    elif sesion_activa["nombre"] and not sesion_activa["demo_finalizada"]:
        respuesta = respuesta_interna(texto)
        ruta = os.path.join(CARPETA_SESIONES, f"{sesion_activa['nombre']}.txt")
        etiqueta = sesion_activa["plan_activo"] or "DEMO"
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M')}] [{etiqueta}] CLIENTE: {texto}\n[{time.strftime('%H:%M')}] [{etiqueta}] MERLÍN: {respuesta}\n\n")
        return respuesta

    return "🧙‍♂️ ¿Cómo te llamo para comenzar?"

def dar_respuesta(mensaje):
    resp = manejar_sesion(mensaje)
    return resp if resp else respuesta_interna(mensaje)

@app.route("/")
def home(): 
    return render_template("index.html")

@app.route('/static/<path:p>')
def st(p): 
    return send_from_directory(app.static_folder, p)

@app.route("/chat", methods=["POST"])
def chat():
    return jsonify({"respuesta": dar_respuesta(request.json.get("mensaje",""))})

if __name__ == "__main__":
    print("✅ MERLÍN MICTROTECH ONLINE | DEMO MODE")
    app.run(host="0.0.0.0", port=14557, debug=False)
