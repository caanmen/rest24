from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import psycopg2

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'jwt_super_secreto'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Configuración para que el token no expire

@app.route('/')

def home():
    return 'Bienvenido a la API de ReservaFacil!'

jwt = JWTManager(app)

def get_db_connection():
    return psycopg2.connect(
        dbname="Restaurante",
        user="postgres",
        password="admin",
        host="localhost"
    )

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

    @app.route('/')

    def home():
        return 'Bienvenido a la API de ReservaFacil!'

@app.route('/mesas', methods=['POST'])
@jwt_required()
def crear_mesa():
    data = request.get_json()
    user_identity = get_jwt_identity()
    user_id = user_identity['user_id']

    if not data or 'personas' not in data or 'localizacion' not in data or 'numero_mesa' not in data:
        return jsonify({"error": "Faltan datos necesarios: personas, localizacion o numero_mesa"}), 400

    personas = data['personas']
    localizacion = data['localizacion']
    numero_mesa = data['numero_mesa']  # Asegurarse de que el número de mesa viene incluido

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SET myapp.current_user_id = %s", [user_id])
    try:
        cursor.execute(
            'INSERT INTO mesas (numero_mesa, personas, localizacion, disponible) VALUES (%s, %s, %s, True) RETURNING numero_mesa;',
            (numero_mesa, personas, localizacion)
        )
        numero_mesa = cursor.fetchone()[0]
        conn.commit()
        return jsonify({"mensaje": "Mesa creada con éxito", "numero_mesa": numero_mesa}), 201
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas/<int:numero_mesa>', methods=['GET'])
@jwt_required()
def obtener_mesa(numero_mesa):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT numero_mesa, personas, localizacion, disponible FROM mesas WHERE numero_mesa = %s;", (numero_mesa,))
        mesa = cursor.fetchone()
        if not mesa:
            return jsonify({"error": "Mesa no encontrada"}), 404
        mesa_info = {
            "numero_mesa": mesa[0],
            "personas": mesa[1],
            "localizacion": mesa[2],
            "disponible": mesa[3]
        }
        return jsonify(mesa_info), 200
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas/<int:numero_mesa>', methods=['DELETE'])
@jwt_required()
def eliminar_mesa(numero_mesa):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM mesas WHERE numero_mesa = %s RETURNING numero_mesa;", (numero_mesa,))
        deleted_mesa = cursor.fetchone()
        if not deleted_mesa:
            return jsonify({"error": "Mesa no encontrada"}), 404
        conn.commit()
        return jsonify({"mensaje": "Mesa eliminada con éxito"}), 200
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas/<int:numero_mesa>', methods=['PUT'])
@jwt_required()
def actualizar_mesa(numero_mesa):
    data = request.get_json()
    personas = data.get('personas')
    localizacion = data.get('localizacion')
    disponible = data.get('disponible', True)  # Por defecto, asumimos que la mesa está disponible

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE mesas SET personas = %s, localizacion = %s, disponible = %s WHERE numero_mesa = %s RETURNING numero_mesa;",
            (personas, localizacion, disponible, numero_mesa)
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
    app.run(debug=True, port=3000)
