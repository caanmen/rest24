from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'jwt_super_secreto'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Configuración para que el token no expire

jwt = JWTManager(app)

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

@app.route('/reservas', methods=['POST'])
@jwt_required()
def crear_reserva():
    data = request.get_json()
    user_identity = get_jwt_identity()
    user_id = user_identity['user_id']

    fecha = data.get('fecha')
    hora = data.get('hora')
    estado = data.get('estado')
    detalle = data.get('detalle')

    if not all([fecha, hora, estado, detalle]):
        return jsonify({"error": "Información incompleta para crear la reserva"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO reservas (fecha, hora, estado, detalle) VALUES (%s, %s, %s, %s) RETURNING id;",
            (fecha, hora, estado, detalle)
        )
        reserva_id = cursor.fetchone()[0]
        conn.commit()
        return jsonify({"mensaje": "Reserva creada con éxito", "reserva_id": reserva_id}), 201
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/update_reserva/<int:reserva_id>', methods=['PUT'])
@jwt_required()
def update_reserva(reserva_id):
    data = request.get_json()
    nuevo_estado = data.get('estado')
    if not nuevo_estado:
        return jsonify({"error": "No se proporcionó el nuevo estado"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE reservas SET estado = %s WHERE id = %s RETURNING id;",
            (nuevo_estado, reserva_id)
        )
        updated_id = cursor.fetchone()
        if updated_id is None:
            return jsonify({"error": "Reserva no encontrada"}), 404
        conn.commit()
        return jsonify({"mensaje": "Estado de la reserva actualizado con éxito"}), 200
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_reserva/<int:reserva_id>', methods=['DELETE'])
@jwt_required()
def delete_reserva(reserva_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM reservas WHERE id = %s RETURNING id;", (reserva_id,))
        deleted_id = cursor.fetchone()
        if deleted_id is None:
            return jsonify({"error": "Reserva no encontrada"}), 404
        conn.commit()
        return jsonify({"mensaje": "Reserva eliminada con éxito"}), 200
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True, port=3100)
