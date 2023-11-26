from flask import Blueprint, request, jsonify
from ..database import db
from sqlalchemy import text

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/', methods=['GET'])
def get_transactions():
    query = text("SELECT * FROM transaction")
    try:
        with db.engine.connect() as connection:
            result = connection.execute(query)
            columns = result.keys()
            rows = [{column: row[i] for i, column in enumerate(columns)} for row in result]

            return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@transaction_bp.route('/add', methods=['POST'])
def add_transaction():
    data = request.get_json()
    type = data.get('type')
    category = data.get('category')
    if not type:
        return jsonify({"error": "Missing transaction type"}), 400

    query = text("""
    INSERT INTO transaction (type, category) 
    VALUES (:type, :category)
    """)

    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"type": type, "category": category})
            connection.commit()
        return jsonify({"message": "Transaction added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@transaction_bp.route('/update/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    data = request.get_json()
    update_fields = {k: v for k, v in data.items() if v is not None and k in ['type', 'category']}
    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    query = text("""
    UPDATE transaction
    SET {} 
    WHERE transactionid = :transaction_id
    """.format(', '.join([f"{key} = :{key}" for key in update_fields])))

    try:
        with db.engine.connect() as connection:
            update_fields['transaction_id'] = transaction_id
            connection.execute(query, update_fields)
            connection.commit()
            return jsonify({"message": "Transaction updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@transaction_bp.route('/delete/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    query = text("DELETE FROM transaction WHERE transactionid = :transaction_id")
    
    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"transaction_id": transaction_id})
            connection.commit()
            return jsonify({"message": "Transaction deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
