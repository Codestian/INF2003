from flask import Blueprint, request, jsonify
from ..database import db
from sqlalchemy import text

frequency_bp = Blueprint('frequency_bp', __name__)

@frequency_bp.route('/', methods=['GET'])
def get_frequencies():
    query = text("SELECT * FROM frequency")
    try:
        with db.engine.connect() as connection:
            result = connection.execute(query)
            columns = result.keys()
            rows = [{column: row[i] for i, column in enumerate(columns)} for row in result]

            return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@frequency_bp.route('/add', methods=['POST'])
def add_frequency():
    data = request.get_json()
    freqtype = data.get('freqtype')
    if not freqtype:
        return jsonify({"error": "Missing frequency type"}), 400

    query = text("""
    INSERT INTO frequency (freqtype) 
    VALUES (:freqtype)
    """)

    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"freqtype": freqtype})
            connection.commit()
        return jsonify({"message": "Frequency added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@frequency_bp.route('/update/<int:freqid>', methods=['PUT'])
def update_frequency(freqid):
    data = request.get_json()
    freqtype = data.get('freqtype')
    if not freqtype:
        return jsonify({"error": "No valid fields to update"}), 400

    query = text("""
    UPDATE frequency
    SET freqtype = :freqtype 
    WHERE freqid = :freqid
    """)

    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"freqtype": freqtype, "freqid": freqid})
            connection.commit()
            return jsonify({"message": "Frequency updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@frequency_bp.route('/delete/<int:freqid>', methods=['DELETE'])
def delete_frequency(freqid):
    query = text("DELETE FROM frequency WHERE freqid = :freqid")
    
    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"freqid": freqid})
            connection.commit()
            return jsonify({"message": "Frequency deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
