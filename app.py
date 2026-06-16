from flask import Flask, render_template, request, redirect, url_for, Response
import os
import requests

app = Flask(__name__)

# ========================================================
# 🤖 CONFIGURACIÓN DE TU BOT DE TELEGRAM
# Reemplaza los textos dentro de las comillas con tus datos reales
TELEGRAM_TOKEN = "8971605974:AAGHKxTujNGUvZW-I6ON2-p-zK-m71b_A7A"
TELEGRAM_CHAT_ID = "6447478231"
# ========================================================

# Base de datos en memoria
bibliografia = []
resultados_busqueda = []
mensaje_alerta = ""

def enviar_alerta_telegram(mensaje_texto):
    """Envía notificaciones a tu celular sin congelar la página web"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": f"🔔 [Alerta Web]: {mensaje_texto}"
        }
        # Usamos timeout bajo (2 segundos) para que si falla Telegram, la página cargue rápido
        requests.post(url, json=payload, timeout=2)
    except Exception as e:
        print(f"Telegram temporalmente no disponible: {e}")

@app.route('/')
def index():
    global mensaje_alerta
    # 🚀 ¡Aquí está la magia! Te avisa al celular cada vez que alguien entra
    enviar_alerta_telegram("¡Alguien acaba de ingresar a tu página del Generador APA!")
    
    alerta = mensaje_alerta
    mensaje_alerta = ""
    return render_template('index.html', bibliografia=bibliografia, resultados=resultados_busqueda, alerta=alerta)

@app.route('/buscar_libro', methods=['POST'])
def buscar_libro():
    """Busca libros en internet usando la API de Google Books"""
    global resultados_busqueda, mensaje_alerta
    resultados_busqueda.clear() 
    
    query = request.form.get('query_busqueda')
    if query:
        # Notificar a tu Telegram qué están buscando en tu web
        enviar_alerta_telegram(f"Están buscando el libro: '{query}'")
        try:
            url = f"https://www.googleapis.com/books/v1/volumes?q={query.strip()}&maxResults=3"
            response = requests.get(url, timeout=6)
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    for item in data["items"]:
                        volume_info = item.get("volumeInfo", {})
                        
                        autores_list = volume_info.get("authors", ["Autor Desconocido"])
                        autores = ", ".join(autores_list)
                        
                        fecha = volume_info.get("publishedDate", "s.f.")
                        anio = fecha.split("-")[0]
                        
                        titulo = volume_info.get("title", "Título Desconocido")
                        
                        resultados_busqueda.append({
                            "autor": autores,
                            "anio": anio,
                            "titulo": titulo
                        })
                    if not resultados_busqueda:
                        mensaje_alerta = "No se encontraron libros. Intenta con otras palabras."
                else:
                    mensaje_alerta = "No hubo resultados para esa búsqueda en Google Books."
            else:
                mensaje_alerta = "El buscador de Google está saturado. Intenta en un momento."
        except Exception as e:
            print(f"Error: {e}")
            mensaje_alerta = "Problema de conexión al buscar. Inténtalo de nuevo."
            
    return redirect(url_for('index'))

@app.route('/generar_cita_automatica', methods=['POST'])
def generar_cita_automatica():
    """Toma el libro seleccionado y crea la cita final"""
    autor = request.form.get('autor')
    anio = request.form.get('anio')
    titulo = request.form.get('titulo')
    
    if autor and anio and titulo:
        cita_lista = f"{autor.strip()} ({anio.strip()}). {titulo.strip()}."
        bibliografia.append({
            "id": len(bibliografia) + 1,
            "texto": cita_lista
        })
        enviar_alerta_telegram(f"¡Se ha generado una nueva cita APA exitosamente!")
    return redirect(url_for('index'))

@app.route('/limpiar_todo')
def limpiar_todo():
    bibliografia.clear()
    resultados_busqueda.clear()
    return redirect(url_for('index'))

@app.route('/exportar_word')
def exportar_word():
    if not bibliografia:
        return redirect(url_for('index'))
    citas_ordenadas = sorted([cita['texto'] for cita in bibliografia])
    contenido = "REFERENCIAS BIBLIOGRÁFICAS (FORMATO APA 7)\n"
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
