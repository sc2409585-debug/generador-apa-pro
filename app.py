from flask import Flask, render_template, request, redirect, url_for, Response
import os
import requests

app = Flask(__name__)

# Base de datos temporal en memoria
bibliografia = []
resultados_busqueda = []
mensaje_alerta = ""  # Para avisarte en pantalla si algo falla

@app.route('/')
def index():
    global mensaje_alerta
    # Guardamos el mensaje en una variable temporal y la limpiamos para la próxima recarga
    alerta = mensaje_alerta
    mensaje_alerta = ""
    return render_template('index.html', bibliografia=bibliografia, resultados=resultados_busqueda, alerta=alerta)

@app.route('/buscar_libro', methods=['POST'])
def buscar_libro():
    """Busca libros reales usando la API pública de Google Books"""
    global resultados_busqueda, mensaje_alerta
    resultados_busqueda.clear() 
    
    query = request.form.get('query_busqueda')
    if query:
        try:
            # Petición directa a Google Books (Trae los 3 libros más relevantes)
            url = f"https://www.googleapis.com/books/v1/volumes?q={query.strip()}&maxResults=3"
            response = requests.get(url, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    for item in data["items"]:
                        volume_info = item.get("volumeInfo", {})
                        
                        # Procesar Autores de forma limpia
                        autores_list = volume_info.get("authors", ["Autor Desconocido"])
                        autores = ", ".join(autores_list)
                        
                        # Procesar Año de publicación
                        fecha = volume_info.get("publishedDate", "s.f.")
                        anio = fecha.split("-")[0] # Extraer solo el año de cuatro dígitos
                        
                        # Procesar Título
                        titulo = volume_info.get("title", "Título Desconocido")
                        
                        resultados_busqueda.append({
                            "autor": autores,
                            "anio": anio,
                            "titulo": titulo
                        })
                    
                    if not resultados_busqueda:
                        mensaje_alerta = "No se encontraron libros con ese título. Intenta con palabras clave."
                else:
                    mensaje_alerta = "Google Books no encontró resultados para esa búsqueda."
            else:
                mensaje_alerta = f"Error de conexión con el buscador (Código {response.status_code})."
                
        except Exception as e:
            print(f"Error en la búsqueda: {e}")
            mensaje_alerta = "Hubo un problema de conexión. Inténtalo de nuevo."
            
    return redirect(url_for('index'))

@app.route('/generar_cita_automatica', methods=['POST'])
def generar_cita_automatica():
    """Toma los datos del libro seleccionado y crea la cita en formato APA 7"""
    autor = request.form.get('autor')
    anio = request.form.get('anio')
    titulo = request.form.get('titulo')
    
    if autor and anio and titulo:
        # Estructura lógica estricta APA 7ma Edición
        cita_lista = f"{autor.strip()} ({anio.strip()}). {titulo.strip()}."
        
        bibliografia.append({
            "id": len(bibliografia) + 1,
            "texto": cita_lista
        })
        
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
