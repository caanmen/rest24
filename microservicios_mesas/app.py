from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import psycopg2

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'jwt_super_secreto'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Configuración para que el token no expire

jwt = JWTManager(app)  # JWTManager se inicializa después de configurar la app

def get_db_connection():
    return psycopg2.connect(
        dbname="Restaurante",
        user="postgres",
        password="admin",
        host="localhost"
    )

@app.route('/')
def home():
    return 'Bienvenido a la API de ReservaFacil!'

@app.route('/login', methods=['POST'])
def login():
    correo = request.json.get('correo', None)
    contrasena = request.json.get('contrasena', None)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE correo = %s AND contrasena = %s", (correo, contrasena))
    user_id = cursor.fetchone()
    cursor.close()
    conn.close()

    if user_id:
        access_token = create_access_token(identity={'user_id': user_id[0]})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401

@app.route('/mesas', methods=['POST'])
@jwt_required()
def crear_mesa():
    data = request.get_json()
    user_identity = get_jwt_identity()

    if not isinstance(user_identity, dict) or 'user_id' not in user_identity:
        return jsonify({'error': 'Usuario no autenticado o JWT malformado'}), 401

    user_id = user_identity['user_id']

    if not data or 'personas' not in data or 'localizacion' not in data or 'numero_mesa' not in data:
        return jsonify({"error": "Faltan datos necesarios: personas, localizacion o numero_mesa"}), 400

    personas = data['personas']
    localizacion = data['localizacion']
    numero_mesa = data['numero_mesa']
    usuario_responsable = user_id  # Asumimos que el usuario que realiza la acción es el responsable

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SET myapp.current_user_id = %s", [user_id])
    try:
        cursor.execute(
            'INSERT INTO mesas (numero_mesa, personas, localizacion, disponible, usuario_responsable) VALUES (%s, %s, %s, True, %s) RETURNING numero_mesa;',
            (numero_mesa, personas, localizacion, usuario_responsable)
        )
        numero_mesa = cursor.fetchone()[0]
        conn.commit()
        return jsonify({"mensaje": "Mesa creada con éxito", "numero_mesa": numero_mesa}), 201
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas/<int:numero_mesa>', methods=['PUT'])
@jwt_required()
def actualizar_mesa(numero_mesa):
    data = request.get_json()
    user_identity = get_jwt_identity()
    user_id = user_identity.get('user_id')

    personas = data.get('personas')
    localizacion = data.get('localizacion')
    disponible = data.get('disponible', True)
    usuario_responsable = user_id  # Asumimos que el usuario que realiza la acción es el responsable

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE mesas SET personas = %s, localizacion = %s, disponible = %s, usuario_responsable = %s WHERE numero_mesa = %s RETURNING numero_mesa;",
            (personas, localizacion, disponible, usuario_responsable, numero_mesa)
        )
        updated_mesa = cursor.fetchone()
        if not updated_mesa:
            return jsonify({"error": "Mesa no encontrada"}), 404
        conn.commit()
        return jsonify({"mensaje": "Mesa actualizada con éxito", "numero_mesa": updated_mesa[0]}), 200
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=3300)
