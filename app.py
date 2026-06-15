from flask import Flask, render_template, request, redirect, url_for, Response
import os
import requests  # Nueva herramienta para conectar con Telegram

app = Flask(__name__)

# ========================================================
# 🤖 CONFIGURACIÓN DE TU BOT DE TELEGRAM
# Pega aquí tus datos reales respetando las comillas
TELEGRAM_TOKEN = "8971605974:AAGHKxTujNGUvZW-I6ON2-p-zK-m71b_A7A"
TELEGRAM_CHAT_ID = "6447478231"
# ========================================================

# Base de datos temporal en memoria para guardar las citas generadas
bibliografia = []

def enviar_alerta_telegram():
    """Función lógica que envía un mensaje a tu Telegram"""
    try:
        mensaje = "🚀 ¡Aviso de Ofimática! Alguien acaba de entrar a tu página web del Generador APA."
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje
        }
        # Python hace la petición oculta a Telegram
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error al enviar a Telegram: {e}")

def generar_apa_libro(autor, anio, titulo):
    """Función lógica que automatiza el formato APA 7ma edición"""
    autor = autor.strip()
    anio = anio.strip()
    titulo = titulo.strip()
    
    cita = f"{autor} ({anio}). {titulo}."
    return cita

@app.route('/')
def index():
    # 🔔 ¡Aquí está la magia! Cuando alguien entra a la raíz '/',
    # el sistema primero te manda el mensaje al cel y luego carga la página.
    enviar_alerta_telegram()
    return render_template('index.html', bibliografia=bibliografia)

@app.route('/generar_cita', methods=['POST'])
def generar_cita():
    autor = request.form.get('autor')
    anio = request.form.get('anio')
    titulo = request.form.get('titulo')
    
    if autor and anio and titulo:
        cita_lista = generar_apa_libro(autor, anio, titulo)
        bibliografia.append({
            "id": len(bibliografia) + 1,
            "texto": cita_lista
        })
    return redirect(url_for('index'))

@app.route('/limpiar_bibliografia')
def limpiar_bibliografia():
    bibliografia.clear()
    return redirect(url_for('index'))

@app.route('/exportar_word')
def exportar_word():
    """Genera un archivo .doc descargable"""
    if not bibliografia:
        return redirect(url_for('index'))
    
    citas_ordenadas = sorted([cita['texto'] for cita in bibliografia])
    
    contenido = "REFERENCIAS BIBLIOGRÁFICAS (FORMATO APA)\n"
    contenido += "========================================\n\n"
    for cita in citas_ordenadas:
        contenido += f"{cita}\n\n"
    
    return Response(
        contenido,
        mimetype="application/msword",
        headers={"Content-disposition": "attachment; filename=bibliografia_apa.doc"}
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
