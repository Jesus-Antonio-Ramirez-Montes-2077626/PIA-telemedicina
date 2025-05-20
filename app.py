# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory
import os
import csv

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'.zip','.dcm'}

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def cargar_usuarios():
    usuarios = []
    with open('Login_and_register.csv', newline='', encoding='utf-8') as csvfile:
        lector = csv.reader(csvfile)
        next(lector)  # saltar encabezado
        for fila in lector:
            usuarios.append(fila)  # [nombre, correo, usuario, contraseña]
    return usuarios

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_usuario = request.form['usuarioCorreo'].strip()
        input_contrasena = request.form['contrasena']

        usuarios = cargar_usuarios()
        encontrado = None
        for u in usuarios:
            if input_usuario == u[1] or input_usuario == u[2]:
                encontrado = u
                break

        if not encontrado:
            return render_template('login.html', error="No está registrado, favor de registrarse")
        if encontrado[3] != input_contrasena:
            return render_template('login.html', error="Buen intento, esa no es la contraseña")

        session['usuario'] = encontrado[2]
        session['nombre'] = encontrado[0]
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    archivos = [f for f in os.listdir(app.config['UPLOAD_FOLDER'])
                if allowed_file(f)]

    return render_template('index.html', nombre=session.get('nombre'), archivos=archivos)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if 'archivo' not in request.files:
        return 'No se envió ningún archivo'

    file = request.files['archivo']
    if file.filename == '':
        return 'Nombre de archivo vacío'

    if not allowed_file(file.filename):
        return 'Solo se permiten archivos .zip'

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return f'Archivo {file.filename} subido correctamente.<br><a href="/">Volver</a>'

@app.route('/download')
def download_file():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    filename = request.args.get('filename')
    if not filename:
        return 'Falta el nombre del archivo'

    if not allowed_file(filename):
        return 'Descarga no permitida'

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # toma el puerto asignado por Render o usa 5000 si no existe
    app.run(host='0.0.0.0', port=port, debug=True)
