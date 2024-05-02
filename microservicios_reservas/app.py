from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import psycopg2
import psycopg2.extras

from datetime import datetime

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

def serialize_reserva(reserva):
    return {
        'id': reserva['id'],
        'fecha': reserva['fecha'].isoformat() if reserva['fecha'] else None,
        'hora': reserva['hora'].strftime('%H:%M:%S') if reserva['hora'] else None,
        'estado': reserva['estado'],
        'detalle': reserva['detalle']
    }

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

    fecha_str = data.get('fecha')
    hora_str = data.get('hora')
    estado = data.get('estado')
    detalle = data.get('detalle')

    # Convertir fecha y hora a objetos apropiados
    try:
        fecha = datetime.strptime(fecha_str, "%d-%m-%Y").date()
        hora = datetime.strptime(hora_str, "%H:%M").time()
    except ValueError as e:
        return jsonify({"error": f"Formato de fecha o hora incorrecto: {str(e)}"}), 400

    if not all([fecha, hora, estado, detalle]):
        return jsonify({"error": "Información incompleta para crear la reserva"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            "INSERT INTO reservas (fecha, hora, estado, detalle) VALUES (%s, %s, %s, %s) RETURNING id, fecha, hora, estado, detalle;",
            (fecha, hora, estado, detalle)
        )
        reserva = cursor.fetchone()
        if not reserva:
            return jsonify({'error': 'Error al crear la reserva'}), 500
        reserva_serializada = serialize_reserva(reserva)
        conn.commit()
        return jsonify({"mensaje": "Reserva creada con éxito", "reserva": reserva_serializada}), 201
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

@app.route('/reservas/fecha', methods=['GET'])
@jwt_required()
def reservas_por_fecha():
    fecha = request.args.get('fecha')
    if not fecha:
        return jsonify({'error': 'Fecha requerida'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT id, fecha, hora, estado, detalle FROM public.reservas WHERE fecha = %s", (fecha,))
        reservas = cursor.fetchall()
        if not reservas:
            return jsonify({'error': 'No se encontraron reservas para esta fecha'}), 404
        reservas_serializadas = [serialize_reserva(reserva) for reserva in reservas]
        return jsonify(reservas_serializadas), 200
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        

if __name__ == '__main__':
    app.run(debug=True, port=3100)
