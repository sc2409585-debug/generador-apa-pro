from flask import Flask, render_template, request, redirect, url_for, Response
import os
import requests

app = Flask(__name__)

# ========================================================
# 🤖 CONFIGURACIÓN DE TU BOT DE TELEGRAM
TELEGRAM_TOKEN = "8971605974:AAGHKxTujNGUvZW-I6ON2-p-zK-m71b_A7A"
TELEGRAM_CHAT_ID = "6447478231"
# ========================================================

# Base de datos temporal en memoria para guardar las citas generadas y resultados de búsqueda
bibliografia = []
resultados_busqueda = []

def enviar_alerta_telegram(mensaje_texto):
    """Función que envía un mensaje a tu Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": f"🚀 [Generador APA Pro]: {mensaje_texto}"
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error al enviar a Telegram: {e}")

@app.route('/')
def index():
    # Avisa a Telegram cuando alguien entra a la página principal
    enviar_alerta_telegram("Alguien ingresó a la plataforma.")
    return render_template('index.html', bibliografia=bibliografia, resultados=resultados_busqueda)

@app.route('/buscar_libro', methods=['POST'])
def buscar_libro():
    """Busca libros reales usando la API pública de Google Books"""
    global resultados_busqueda
    resultados_busqueda.clear() # Limpiar búsquedas anteriores
    
    query = request.form.get('query_busqueda')
    if query:
        enviar_alerta_telegram(f"Buscando el libro: '{query}'")
        try:
            # Petición lógica al servidor de Google Books
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=3"
            response = requests.get(url, timeout=5).json()
            
            # Procesar los resultados encontrados
            if "items" in response:
                for item in response["items"]:
                    volume_info = item.get("volumeInfo", {})
                    
                    # Extraer Autores
                    autores_list = volume_info.get("authors", ["Autor Desconocido"])
                    autores = ", ".join(autores_list)
                    
                    # Extraer Año de publicación
                    fecha = volume_info.get("publishedDate", "s.f.")
                    anio = fecha.split("-")[0] # Extrae solo el año si viene la fecha completa
                    
                    # Extraer Título
                    titulo = volume_info.get("title", "Título Desconocido")
                    
                    resultados_busqueda.append({
                        "autor": autores,
                        "anio": anio,
                        "titulo": titulo
                    })
        except Exception as e:
            print(f"Error en la búsqueda: {e}")
            
    return redirect(url_for('index'))

@app.route('/generar_cita_automatica', methods=['POST'])
def generar_cita_automatica():
    """Toma los datos del libro seleccionado y crea la cita en formato APA 7"""
    autor = request.form.get('autor')
    anio = request.form.get('anio')
    titulo = request.form.get('titulo')
    
    if autor and anio and titulo:
        # Lógica estricta de formato APA: Autor (Año). Título.
        cita_lista = f"{autor.strip()} ({anio.strip()}). {titulo.strip()}."
        
        bibliografia.append({
            "id": len(bibliografia) + 1,
            "texto": cita_lista
        })
        enviar_alerta_telegram(f"¡Nueva cita APA generada con éxito!")
        
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
