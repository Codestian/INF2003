from flask import Blueprint, request, jsonify
from ..database import db
from sqlalchemy import text

assettype_bp = Blueprint('assettype_bp', __name__)

@assettype_bp.route('/', methods=['GET'])
def get_assettypes():
    query = text("SELECT * FROM assettype")
    try:
        with db.engine.connect() as connection:
            result = connection.execute(query)
            columns = result.keys()
            rows = [{column: row[i] for i, column in enumerate(columns)} for row in result]

            return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@assettype_bp.route('/add', methods=['POST'])
def add_assettype():
    data = request.get_json()
    type = data.get('type')

    if not type:
        return jsonify({"error": "Missing asset type"}), 400

    query = text("""
    INSERT INTO assettype (type) 
    VALUES (:type)
    """)

    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"type": type})
            connection.commit()
        return jsonify({"message": "Asset type added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@assettype_bp.route('/update/<int:assettypeid>', methods=['PUT'])
def update_assettype(assettypeid):
    data = request.get_json()
    type = data.get('type')

    if not type:
        return jsonify({"error": "No valid type to update"}), 400

    query = text("""
    UPDATE assettype
    SET type = :type 
    WHERE assettypeid = :assettypeid
    """)

    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"type": type, "assettypeid": assettypeid})
            connection.commit()
            return jsonify({"message": "Asset type updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@assettype_bp.route('/delete/<int:assettypeid>', methods=['DELETE'])
def delete_assettype(assettypeid):
    query = text("DELETE FROM assettype WHERE assettypeid = :assettypeid")
    
    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"assettypeid": assettypeid})
            connection.commit()
            return jsonify({"message": "Asset type deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
