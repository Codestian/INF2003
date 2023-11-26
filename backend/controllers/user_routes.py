from flask import Blueprint, request, jsonify
from ..database import db
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
from flask import jsonify

SECRET_KEY = "your_secret_key"

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    query = text("SELECT * FROM users WHERE email = :email")
    try:
        with db.engine.connect() as connection:
            result = connection.execute(query, {"email":email}).fetchone()
            if result is None:
                return jsonify({"error": "User not found"}), 404

            stored_password = result[3]  
            if check_password_hash(stored_password, password):
                token = generate_token(result[0]) 
                return jsonify({'token': token}), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/', methods=['GET'])
def get_users():
    query = text("SELECT * FROM users")
    try:
        with db.engine.connect() as connection:
            result = connection.execute(query)
            columns = result.keys()
            rows = [{column: row[i] for i, column in enumerate(columns)} for row in result]

            return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@user_bp.route('/add', methods=['POST'])
def add_user():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({"error": "Missing data"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    query = text("""
    INSERT INTO users (email, username, password) 
    VALUES (:email, :username, :password)
    """)

    try:
        with db.engine.connect() as connection:
            # Insert user data with hashed password
            connection.execute(query, {"email": email, "username": username, "password": hashed_password})
            connection.commit()
            # In SQLAlchemy, commit is usually not needed for single operations like this
            return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.route('/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    # Prepare the update fields dynamically
    update_fields = {k: v for k, v in data.items() if v is not None and k in ['email', 'username', 'password']}
    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    query = text("""
    UPDATE users
    SET {} 
    WHERE userid = :user_id
    """.format(', '.join([f"{key} = :{key}" for key in update_fields])))

    try:
        with db.engine.connect() as connection:
            update_fields['user_id'] = user_id
            connection.execute(query, update_fields)
            connection.commit()
            return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@user_bp.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    query = text("DELETE FROM users WHERE userid = :user_id")
    
    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"user_id": user_id})
            connection.commit()
            return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def generate_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),  # Token expiration time
        'iat': datetime.datetime.utcnow(),  # Time the token is generated
        'sub': user_id  # Subject of the token (user_id)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256') 