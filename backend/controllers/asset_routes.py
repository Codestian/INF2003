from flask import Blueprint, request, jsonify
from ..database import db
from sqlalchemy import text
import jwt

asset_bp = Blueprint('asset_bp', __name__)

SECRET_KEY = "your_secret_key"

@asset_bp.route('/', methods=['GET'])
def get_assets():
    query = text("SELECT * FROM assets")
    try:
        with db.engine.connect() as connection:
            result = connection.execute(query)
            columns = result.keys()
            rows = [{column: row[i] for i, column in enumerate(columns)} for row in result]

            return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@asset_bp.route('/user', methods=['GET'])
def get_assets_by_user():
    # Retrieve the token from the Authorization header
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Missing JWT token"}), 401

    # Optional: Remove 'Bearer ' prefix if it exists
    if token.startswith('Bearer '):
        token = token[7:]

    try:
        # Attempt to decode the token
        decoded = jwt.decode(token, "your_secret_key", algorithms=["HS256"])

        # Token is valid, proceed to fetch assets
        query = text("""
        SELECT 
            assetid, 
            name, 
            value, 
            amount, 
            assettypeid, 
            date, 
            userid, 
            purchaseprice,
            value * amount AS total_value, 
            ((value * amount) - (purchaseprice * amount)) / (purchaseprice * amount) * 100 AS profit_percentage
        FROM 
            assets
        WHERE 
            userid = :userid;
        """)

        with db.engine.connect() as connection:
            result = connection.execute(query, {'userid': decoded['sub']})
            columns = result.keys()
            rows = [{column: row[i] for i, column in enumerate(columns)} for row in result]

            return jsonify(rows), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@asset_bp.route('/add', methods=['POST'])
def add_asset():
    data = request.get_json()
    name = data.get('name')
    value = data.get('value')
    amount = data.get('amount')
    assettypeid = data.get('assettypeid')
    date = data.get('date')
    userid = data.get('userid')
    purchaseprice = data.get('purchaseprice')

    if not name or value is None or amount is None or purchaseprice is None:
        return jsonify({"error": "Missing required data"}), 400

    query = text("""
    INSERT INTO assets (name, value, amount, assettypeid, date, userid, purchaseprice) 
    VALUES (:name, :value, :amount, :assettypeid, :date, :userid, :purchaseprice)
    """)

    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"name": name, "value": value, "amount": amount, "assettypeid": assettypeid, 
                                       "date": date, "userid": userid, "purchaseprice": purchaseprice})
            connection.commit()
        return jsonify({"message": "Asset added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@asset_bp.route('/update/<int:assetid>', methods=['PUT'])
def update_asset(assetid):
    data = request.get_json()
    update_fields = {k: v for k, v in data.items() if v is not None and k in ['name', 'value', 'amount', 'assettypeid', 'date', 'userid', 'purchaseprice']}
    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    query_parts = [f"{key} = :{key}" for key in update_fields]
    query = text("""
    UPDATE assets
    SET {} 
    WHERE assetid = :assetid
    """.format(', '.join(query_parts)))

    try:
        with db.engine.connect() as connection:
            update_fields['assetid'] = assetid
            connection.execute(query, update_fields)
            connection.commit()
            return jsonify({"message": "Asset updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@asset_bp.route('/delete/<int:assetid>', methods=['DELETE'])
def delete_asset(assetid):
    query = text("DELETE FROM assets WHERE assetid = :assetid")
    
    try:
        with db.engine.connect() as connection:
            connection.execute(query, {"assetid": assetid})
            connection.commit()
            return jsonify({"message": "Asset deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
