from flask import Blueprint, request, jsonify
from ..database import db
from sqlalchemy import text

expense_bp = Blueprint('expense_bp', __name__)

@expense_bp.route('/', methods=['GET'])
def get_expenses():
    query = text("SELECT * FROM expenses")
    try:
        with db.engine.connect() as connection:
            result = connection.execute(query)
            columns = result.keys()
            rows = [{column: row[i] for i, column in enumerate(columns)} for row in result]

            return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@expense_bp.route('/add', methods=['POST'])
def add_expense():
    data = request.get_json()
    name = data.get('name')
    value = data.get('value')
    transactionid = data.get('transactionid')
    datepurchased = data.get('datepurchased')
    userid = data.get('userid')
    frequency = data.get('frequency')
    nextdue = data.get('nextdue')

    if not name or value is None:
        return jsonify({"error": "Missing required data"}), 400

    query = text("""
    INSERT INTO expenses (name, value, transactionid, datepurchased, userid, frequency, nextdue) 
    VALUES (:name, :value, :transactionid, :datepurchased, :userid, :frequency, :nextdue)
    """)

    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"name": name, "value": value, "transactionid": transactionid, 
                                       "datepurchased": datepurchased, "userid": userid, "frequency": frequency, "nextdue": nextdue})
            connection.commit()
        return jsonify({"message": "Expense added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@expense_bp.route('/update/<int:expenseId>', methods=['PUT'])
def update_expense(expenseId):
    data = request.get_json()
    update_fields = {k: v for k, v in data.items() if v is not None and k in ['name', 'value', 'transactionid', 'datepurchased', 'userid', 'frequency', 'nextdue']}
    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    query_parts = [f"{key} = :{key}" for key in update_fields]
    query = text("""
    UPDATE expenses
    SET {} 
    WHERE expenseId = :expenseId
    """.format(', '.join(query_parts)))

    try:
        with db.engine.connect() as connection:
            update_fields['expenseId'] = expenseId
            connection.execute(query, update_fields)
            connection.commit()
            return jsonify({"message": "Expense updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@expense_bp.route('/delete/<int:expenseId>', methods=['DELETE'])
def delete_expense(expenseId):
    query = text("DELETE FROM expenses WHERE expenseId = :expenseId")
    
    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"expenseId": expenseId})
            connection.commit()
            return jsonify({"message": "Expense deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
