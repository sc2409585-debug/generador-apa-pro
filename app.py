from flask import Flask, render_template, request, redirect, url_for, Response
import os

app = Flask(__name__)

# Base de datos temporal en memoria para guardar las citas generadas
bibliografia = []

def generar_apa_libro(autor, anio, titulo):
    """Función lógica que automatiza el formato APA 7ma edición"""
    autor = autor.strip()
    anio = anio.strip()
    titulo = titulo.strip()
    
    cita = f"{autor} ({anio}). {titulo}."
    return cita

@app.route('/')
def index():
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
