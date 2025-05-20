# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory
import os
import csv

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'.zip', '.dcm'}

# Ruta absoluta del CSV en la raíz del proyecto
CSV_PATH = os.path.join(os.getcwd(), 'Login_and_register.csv')

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def cargar_usuarios():
    usuarios = []
    if not os.path.exists(CSV_PATH):
        # Crear archivo CSV con encabezado si no existe
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            escritor = csv.writer(csvfile)
            escritor.writerow(['nombre', 'correo', 'usuario', 'contrasena'])
        return usuarios

    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        lector = csv.reader(csvfile)
        next(lector)  # saltar encabezado
        for fila in lector:
            usuarios.append(fila)  # [nombre, correo, usuario, contraseña]
    return usuarios

# Página principal de bienvenida con opción a login o registro
@app.route('/')
def inicio():
    return render_template('inicio.html')  # Página que ofrece elegir Login o Registro

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
        return redirect(url_for('index'))  # Panel de usuario

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        correo = request.form['correo'].strip()
        usuario = request.form['usuario'].strip()
        contrasena = request.form['contrasena'].strip()

        usuarios = cargar_usuarios()
        for u in usuarios:
            if correo == u[1] or usuario == u[2]:
                return render_template('register.html', error="Usuario o correo ya registrado.")

        # Añadir nuevo usuario al CSV en modo append
        with open(CSV_PATH, 'a', newline='', encoding='utf-8') as csvfile:
            escritor = csv.writer(csvfile)
            escritor.writerow([nombre, correo, usuario, contrasena])

        return redirect(url_for('login'))

    return render_template('register.html')

# Ruta del panel del usuario con lista de archivos permitidos
@app.route('/panel')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    archivos = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
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
        return 'Solo se permiten archivos .zip o .dcm'

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return f'Archivo {file.filename} subido correctamente.<br><a href="/panel">Volver</a>'

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
    return redirect(url_for('inicio'))  # Volver a la página principal

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Usar puerto asignado o 5000 por defecto
    app.run(host='0.0.0.0', port=port, debug=True)
