import os
from extensions import db

def init_db(app):
    try:
        db_path = os.path.join(app.instance_path, 'app.sqlite')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        os.makedirs(app.instance_path, exist_ok=True)

        with app.app_context():
            db.create_all()
            create_admin_user(app)
    except Exception as e:
        app.logger.error(f"An error occurred while initializing the database: {e}")

def create_admin_user(app):
    from models import User  # Import here to avoid circular import

    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    admin_name = os.environ.get('ADMIN_NAME')
    admin_phone = os.environ.get('ADMIN_PHONE')
    admin_address = os.environ.get('ADMIN_ADDRESS')

    if not all([admin_email, admin_password, admin_name, admin_phone, admin_address]):
        app.logger.warning("Admin user environment variables not set. Skipping admin user creation.")
        return

    existing_admin = User.query.filter_by(email=admin_email).first()
    if existing_admin:
        app.logger.info("Admin user already exists. Skipping admin user creation.")
        return

    admin_user = User(
        email=admin_email,
        name=admin_name,
        phone=admin_phone,
        address=admin_address,
        is_admin=True
    )
    admin_user.set_password(admin_password)

    db.session.add(admin_user)
    db.session.commit()
    app.logger.info("Admin user created successfully.")