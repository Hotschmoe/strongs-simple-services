from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_db(app):
    try:
        db_path = os.path.join(app.instance_path, 'app.sqlite')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        os.makedirs(app.instance_path, exist_ok=True)

        with app.app_context():
            db.create_all()
    except Exception as e:
        app.logger.error(f"An error occurred while initializing the database: {e}")
        # Handle the error appropriately (e.g., exit the application or use a fallback)