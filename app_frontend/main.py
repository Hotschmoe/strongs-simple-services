from flask import Flask, render_template, g, redirect, url_for, request, flash, session, jsonify, send_from_directory, send_file
import uuid
from database import init_db
from extensions import db, migrate
from models import User, Order
import qrcode
import io
import base64
import json
import os
from datetime import datetime, timedelta
import shutil
import werkzeug
from werkzeug.utils import secure_filename
from flask_migrate import upgrade, current
import subprocess
from pathlib import Path

app = Flask(__name__)
init_db(app)
migrate.init_app(app, db)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

# Load business configuration
config_path = os.environ.get('BUSINESS_CONFIG_PATH', '/app/business_config.json')
try:
    with open(config_path) as config_file:
        business_config = json.load(config_file)
except FileNotFoundError:
    app.logger.error(f"Business configuration file not found at {config_path}")
    business_config = {
        "businessName": "Default Business",
        "businessDescription": "Default description",
        "services": []
    }
except json.JSONDecodeError:
    app.logger.error(f"Invalid JSON in business configuration file at {config_path}")
    business_config = {
        "businessName": "Default Business",
        "businessDescription": "Default description",
        "services": []
    }

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            g.user = user
    g.business_config = business_config

@app.route('/')
def index():
    return redirect(url_for('homepage'))

@app.route('/index')
def index_page():
    return render_template('index.html', business_config=business_config)

@app.route('/homepage')
def homepage():
    return render_template('homepage.html', business_config=business_config)

@app.route('/order-service')
def order_service():
    if not g.user:
        flash('Please log in to place an order.', 'warning')
        return redirect(url_for('login'))
    return render_template('order_service.html', user=g.user, business_config=business_config)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not g.user:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']

        g.user.name = name
        g.user.phone = phone
        g.user.address = address

        db.session.commit()

        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=g.user, business_config=business_config)

@app.route('/dashboard')
def dashboard():
    if not g.user or not g.user.is_admin:
        flash('You do not have permission to access the dashboard.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    orders = Order.query.join(User).all()
    return render_template('dashboard.html', users=users, orders=orders, business_config=business_config)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', user=g.user, business_config=business_config)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email, phone=phone, address=address)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', user=g.user, business_config=business_config)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/place_order', methods=['POST'])
def place_order():
    if not g.user:
        return jsonify({'error': 'User not logged in'}), 401

    service_type = request.form.get('service_type')
    quantity = float(request.form.get('quantity'))
    total = request.form.get('total')

    order_id = str(uuid.uuid4())

    new_order = Order(
        id=order_id,
        user_id=g.user.id,
        service_type=service_type,
        quantity=quantity,
        total=total,
        status='Pending'
    )
    db.session.add(new_order)
    db.session.commit()

    return jsonify({'order_id': order_id}), 200

@app.route('/qr-code')
def qr_code():
    if not g.user or not g.user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    current_domain = request.host_url.rstrip('/')
    order_url = f"{current_domain}/order-service"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(order_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('qr_code.html', qr_code=img_str, business_config=business_config)

@app.route('/robots.txt') # This is for google to index the site
def robots_txt():
    return send_from_directory(app.static_folder, 'robots.txt')

# Add these new routes
@app.route('/api/order/<order_id>/complete', methods=['POST'])
def complete_order(order_id):
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    order = Order.query.get_or_404(order_id)
    order.status = 'Completed'
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/order/<order_id>/receipt', methods=['GET'])
def get_receipt(order_id):
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    order = Order.query.get_or_404(order_id)
    receipt_data = {
        'order_id': order.id,
        'customer': order.user.name,
        'service_type': order.service_type,
        'quantity': order.quantity,
        'total': order.total,
        'date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'business_name': business_config['businessName']
    }
    
    return jsonify(receipt_data)

@app.route('/api/user/<user_id>', methods=['GET', 'PUT'])
def manage_user(user_id):
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'address': user.address,
            'is_admin': user.is_admin,
            'is_active': user.is_active
        })
    
    elif request.method == 'PUT':
        data = request.json
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        user.phone = data.get('phone', user.phone)
        user.address = data.get('address', user.address)
        user.is_admin = data.get('is_admin', user.is_admin)
        user.is_active = data.get('is_active', user.is_active)
        
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/order/<order_id>', methods=['GET', 'PUT'])
def manage_order(order_id):
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': order.id,
            'service_type': order.service_type,
            'quantity': order.quantity,
            'total': order.total,
            'status': order.status
        })
    
    elif request.method == 'PUT':
        data = request.json
        order.service_type = data.get('service_type', order.service_type)
        order.quantity = data.get('quantity', order.quantity)
        order.total = data.get('total', order.total)
        order.status = data.get('status', order.status)
        
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/backup', methods=['POST'])
def backup_database():
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(app.instance_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'app_backup_{timestamp}.sqlite'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy the database file
        db_path = os.path.join(app.instance_path, 'app.sqlite')
        shutil.copy2(db_path, backup_path)
        
        return jsonify({'success': True, 'filename': backup_filename})
    except Exception as e:
        app.logger.error(f"Backup failed: {str(e)}")
        return jsonify({'error': 'Backup failed'}), 500

@app.route('/api/backup-download', methods=['POST'])
def backup_and_download():
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Create backup
        backup_dir = os.path.join(app.instance_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'app_backup_{timestamp}.sqlite'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy the database file
        db_path = os.path.join(app.instance_path, 'app.sqlite')
        shutil.copy2(db_path, backup_path)
        
        # Send the file
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=backup_filename,
            mimetype='application/x-sqlite3'
        )
    except Exception as e:
        app.logger.error(f"Backup and download failed: {str(e)}")
        return jsonify({'error': 'Backup and download failed'}), 500

@app.route('/api/restore', methods=['POST'])
def restore_database():
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        if 'backup_file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['backup_file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.sqlite'):
            return jsonify({'error': 'Invalid file type. Must be a .sqlite file'}), 400
        
        # Create a temporary directory for validation
        temp_dir = os.path.join(app.instance_path, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save and validate the uploaded file
        temp_path = os.path.join(temp_dir, 'temp_backup.sqlite')
        file.save(temp_path)
        
        # Validate that this is a valid SQLite database
        try:
            import sqlite3
            conn = sqlite3.connect(temp_path)
            # Check if essential tables exist
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            required_tables = {'user', 'order'}  # Add your essential tables here
            if not required_tables.issubset(set(tables)):
                raise Exception("Invalid database structure")
            conn.close()
        except Exception as e:
            os.remove(temp_path)
            return jsonify({'error': 'Invalid database file'}), 400
        
        # Backup the current database before replacing
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        auto_backup_filename = f'auto_backup_before_restore_{timestamp}.sqlite'
        backup_dir = os.path.join(app.instance_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        current_db_path = os.path.join(app.instance_path, 'app.sqlite')
        shutil.copy2(current_db_path, os.path.join(backup_dir, auto_backup_filename))
        
        # Replace the current database with the uploaded one
        shutil.copy2(temp_path, current_db_path)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'message': 'Database restored successfully',
            'auto_backup': auto_backup_filename
        })
        
    except Exception as e:
        app.logger.error(f"Restore failed: {str(e)}")
        return jsonify({'error': f'Restore failed: {str(e)}'}), 500

@app.route('/api/migrate', methods=['POST'])
def run_migration():
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Create automatic backup before migration
        backup_dir = os.path.join(app.instance_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'pre_migration_backup_{timestamp}.sqlite'
        backup_path = os.path.join(backup_dir, backup_filename)
        db_path = os.path.join(app.instance_path, 'app.sqlite')
        shutil.copy2(db_path, backup_path)

        # Run migrations
        with app.app_context():
            # Get current version before upgrade
            old_version = current()
            
            # Run the upgrade
            upgrade()
            
            # Get new version after upgrade
            new_version = current()

        message = f"Migration completed successfully.\n"
        message += f"Previous version: {old_version or 'Initial'}\n"
        message += f"New version: {new_version or 'Initial'}\n"
        message += f"Backup created: {backup_filename}"

        return jsonify({
            'success': True,
            'message': message,
            'backup': backup_filename
        })

    except Exception as e:
        app.logger.error(f"Migration failed: {str(e)}")
        return jsonify({'error': f'Migration failed: {str(e)}'}), 500

@app.route('/api/db-version')
def get_db_version():
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        with app.app_context():
            version = current()
        return jsonify({'version': str(version) if version else 'Initial'})
    except Exception as e:
        app.logger.error(f"Error getting DB version: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
