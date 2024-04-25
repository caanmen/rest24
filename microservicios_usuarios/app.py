from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
import psycopg2
import psycopg2.extras




# Creación de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'tu_super_secreto'
app.config['JWT_SECRET_KEY'] = 'jwt_super_secreto'
jwt = JWTManager(app)

class DatabaseConnection:
    connection = None

    @staticmethod
    def get_connection():
        if DatabaseConnection.connection is None:
            DatabaseConnection.connection = psycopg2.connect(
                dbname="Restaurante",
                user="postgres",
                password="admin",
                host="localhost"
            )
        return DatabaseConnection.connection

def get_db_connection():
    return DatabaseConnection.get_connection()

@app.route('/')

def home():
    return 'Bienvenido a la API de ReservaFacil!'

@app.route('/login', methods=['POST'])
def login():
    credentials = request.json
    correo = credentials['correo']
    contrasena = credentials['contrasena']

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(
            'SELECT * FROM public.usuarios WHERE correo = %s AND contrasena = %s',
            (correo, contrasena)
        )
        user = cursor.fetchone()
        if user:
            access_token = create_access_token(identity=user['correo'])
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/create_user', methods=['POST'])
def create_user():
    user_details = request.json
    nombre = user_details['nombre']
    apellido = user_details['apellido']
    correo = user_details['correo']
    telefono = user_details['telefono']
    tipo_usuario = user_details['tipo_usuario']
    contrasena = user_details['contrasena']

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO public.usuarios (nombre, apellido, correo, telefono, tipo_usuario, contrasena) VALUES (%s, %s, %s, %s, %s, %s)',
            (nombre, apellido, correo, telefono, tipo_usuario, contrasena)
        )
        conn.commit()
        return jsonify({'message': 'Usuario creado exitosamente'}), 201
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=3200)
