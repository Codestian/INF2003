from flask import Blueprint, request, jsonify
from ..database import db
from sqlalchemy import text

income_bp = Blueprint('income_bp', __name__)

@income_bp.route('/', methods=['GET'])
def get_incomes():
    query = text("SELECT * FROM income")
    try:
        with db.engine.connect() as connection:
            result = connection.execute(query)
            columns = result.keys()
            rows = [{column: row[i] for i, column in enumerate(columns)} for row in result]

            return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@income_bp.route('/add', methods=['POST'])
def add_income():
    data = request.get_json()
    name = data.get('name')
    value = data.get('value')
    transactionid = data.get('transactionid')
    datepurchased = data.get('datepurchased')
    userid = data.get('userid')
    freqid = data.get('freqid')
    nextdue = data.get('nextdue')

    if not name or value is None:
        return jsonify({"error": "Missing required data"}), 400

    query = text("""
    INSERT INTO income (name, value, transactionid, datepurchased, userid, freqid, nextdue) 
    VALUES (:name, :value, :transactionid, :datepurchased, :userid, :freqid, :nextdue)
    """)

    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"name": name, "value": value, "transactionid": transactionid, 
                                       "datepurchased": datepurchased, "userid": userid, "freqid": freqid, "nextdue": nextdue})
            connection.commit()
        return jsonify({"message": "Income added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@income_bp.route('/update/<int:incomeid>', methods=['PUT'])
def update_income(incomeid):
    data = request.get_json()
    update_fields = {k: v for k, v in data.items() if v is not None and k in ['name', 'value', 'transactionid', 'datepurchased', 'userid', 'freqid', 'nextdue']}
    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    query_parts = [f"{key} = :{key}" for key in update_fields]
    query = text("""
    UPDATE income
    SET {} 
    WHERE incomeid = :incomeid
    """.format(', '.join(query_parts)))

    try:
        with db.engine.connect() as connection:
            update_fields['incomeid'] = incomeid
            connection.execute(query, update_fields)
            connection.commit()
            return jsonify({"message": "Income updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@income_bp.route('/delete/<int:incomeid>', methods=['DELETE'])
def delete_income(incomeid):
    query = text("DELETE FROM income WHERE incomeid = :incomeid")
    
    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"incomeid": incomeid})
            connection.commit()
            return jsonify({"message": "Income deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
