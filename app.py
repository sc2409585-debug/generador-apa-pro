@app.route('/buscar_libro', methods=['POST'])
def buscar_libro():
    """Busca libros en internet usando la API de Google Books de forma segura"""
    global resultados_busqueda, mensaje_alerta
    resultados_busqueda.clear() 
    
    query = request.form.get('query_busqueda')
    if query:
        # Notificar a tu Telegram qué están buscando en tu web
        enviar_alerta_telegram(f"Están buscando el libro: '{query}'")
        try:
            url = f"https://www.googleapis.com/books/v1/volumes?q={query.strip()}&maxResults=3"
            
            # 🕵️ SIMULAR UN NAVEGADOR REAL PARA QUE GOOGLE NO BLOQUEE LA PETICIÓN
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=8)
            
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
                        mensaje_alerta = "No se encontraron libros. Intenta con otras palabras clave."
                else:
                    mensaje_alerta = "No hubo resultados para esa búsqueda en Google Books."
            else:
                # Si el código no es 200, te mostrará el error exacto en pantalla para saber qué dice Google
                mensaje_alerta = f"Google Books respondió con código de protección {response.status_code}."
                
        except Exception as e:
            print(f"Error: {e}")
            mensaje_alerta = "Problema de conexión al buscar. Inténtalo de nuevo."
            
    return redirect(url_for('index'))
