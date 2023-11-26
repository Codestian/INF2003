from flask import Flask
from flask_cors import CORS

from sqlalchemy import inspect
from backend.setup_database import create_tables
from backend.controllers.user_routes import user_bp
from backend.controllers.transaction_routes import transaction_bp
from backend.controllers.frequency_routes import frequency_bp
from backend.controllers.income_routes import income_bp
from backend.controllers.expense_routes import expense_bp
from backend.controllers.asset_routes import asset_bp
from backend.controllers.assettype_routes import assettype_bp

from .database import db

def create_app():
    app = Flask(__name__)
    CORS(app)

    with app.app_context():
        # Check if any table exists
        inspector = inspect(db.engine)
        tables_exist = inspector.get_table_names()

        # If no tables exist, create them
        if not tables_exist:
            create_tables(db)

        app.register_blueprint(user_bp, url_prefix='/users')
        app.register_blueprint(transaction_bp, url_prefix='/transaction')
        app.register_blueprint(frequency_bp, url_prefix='/frequency')
        app.register_blueprint(income_bp, url_prefix='/income')
        app.register_blueprint(expense_bp, url_prefix='/expense')
        app.register_blueprint(asset_bp, url_prefix='/asset')
        app.register_blueprint(assettype_bp, url_prefix='/assettype')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000)
