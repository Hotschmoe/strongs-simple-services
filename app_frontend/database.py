import os
import sqlite3
from extensions import db
import logging

def init_db(app):
    try:
        db_path = os.path.join(app.instance_path, 'app.sqlite')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        os.makedirs(app.instance_path, exist_ok=True)
        
        # Check if database exists and needs updating
        if os.path.exists(db_path):
            update_database_schema(app, db_path)
        else:
            # New installation, create fresh database
            with app.app_context():
                db.create_all()
                create_admin_user(app)
                
    except Exception as e:
        app.logger.error(f"An error occurred while initializing the database: {e}")

def update_database_schema(app, db_path):
    try:
        # Create backup before making changes
        backup_path = f"{db_path}.backup"
        import shutil
        shutil.copy2(db_path, backup_path)
        app.logger.info(f"Created database backup at {backup_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check existing tables and columns
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {table[0] for table in cursor.fetchall()}

        # Update User table if needed
        if 'user' in existing_tables:
            columns = [col[1] for col in cursor.execute('PRAGMA table_info(user)').fetchall()]
            
            # Add new columns if they don't exist
            if 'is_subscriber' not in columns:
                cursor.execute('ALTER TABLE user ADD COLUMN is_subscriber BOOLEAN DEFAULT 0')
            if 'subscription_end_date' not in columns:
                cursor.execute('ALTER TABLE user ADD COLUMN subscription_end_date DATETIME DEFAULT NULL')

        # Update Order table if needed
        if 'order' in existing_tables:
            columns = [col[1] for col in cursor.execute('PRAGMA table_info("order")').fetchall()]
            
            new_columns = [
                ('is_subscription', 'BOOLEAN DEFAULT 0'),
                ('subscription_period', 'VARCHAR DEFAULT NULL'),
                ('subscription_start_date', 'DATETIME DEFAULT NULL'),
                ('subscription_end_date', 'DATETIME DEFAULT NULL'),
                ('services_per_period', 'INTEGER DEFAULT NULL')
            ]
            
            for col_name, col_type in new_columns:
                if col_name not in columns:
                    cursor.execute(f'ALTER TABLE "order" ADD COLUMN {col_name} {col_type}')

        # Create SubscriptionUsage table if it doesn't exist
        if 'subscription_usage' not in existing_tables:
            cursor.execute('''
                CREATE TABLE subscription_usage (
                    id INTEGER PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    period_start DATETIME NOT NULL,
                    period_end DATETIME NOT NULL,
                    services_allowed INTEGER NOT NULL,
                    services_used INTEGER DEFAULT 0,
                    FOREIGN KEY (order_id) REFERENCES "order" (id)
                )
            ''')

        conn.commit()
        conn.close()
        app.logger.info("Database schema updated successfully")

    except Exception as e:
        app.logger.error(f"Error updating database schema: {e}")
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, db_path)
            app.logger.info("Restored database from backup after failed update")
        raise

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