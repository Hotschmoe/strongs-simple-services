from flask import Flask, render_template, g, redirect, url_for, request, flash, session, jsonify, send_from_directory, send_file
import uuid
from database import init_db
from extensions import db
from models import User, Order, Subscription
import qrcode
import io
import base64
import json
import os
from datetime import datetime, timedelta
import shutil
import werkzeug
from werkzeug.utils import secure_filename
import subprocess
from pathlib import Path
import stripe
from dotenv import load_dotenv

# Get the parent directory of the current file's directory
root_dir = Path(__file__).resolve().parent.parent

# Load environment variables from .env file in parent directory
load_dotenv(root_dir / '.env')

app = Flask(__name__)
init_db(app)
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
        return redirect(url_for('login'))
    
    selected_plan = request.args.get('plan', 'oneTime')
    stripe_public_key = None
    
    if business_config['paymentSettings'].get('stripeEnabled', False):
        stripe_public_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        if not stripe_public_key:
            app.logger.error("Stripe public key not found in environment variables")
            flash('Card payment service is currently unavailable', 'error')

    return render_template('order_service.html', 
                         business_config=business_config,
                         selected_plan=selected_plan,
                         stripe_public_key=stripe_public_key)

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

    # Add current datetime for subscription comparison
    now = datetime.utcnow()
    return render_template('profile.html', 
                         user=g.user, 
                         business_config=business_config,
                         now=now)

@app.route('/dashboard')
def dashboard():
    if not g.user or not g.user.is_admin:
        flash('You do not have permission to access the dashboard.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    active_orders = Order.query.filter(Order.status != 'Completed').join(User).all()
    completed_orders = Order.query.filter(Order.status == 'Completed').join(User).all()
    active_subscriptions = Subscription.query.filter(Subscription.status == 'active').join(User).all()
    canceled_subscriptions = Subscription.query.filter(Subscription.status == 'canceled').join(User).all()

    return render_template('dashboard.html', 
                           users=users, 
                           active_orders=active_orders, 
                           completed_orders=completed_orders,
                           active_subscriptions=active_subscriptions,
                           canceled_subscriptions=canceled_subscriptions,
                           business_config=business_config)

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
    if not g.user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    order = Order.query.get_or_404(order_id)
    
    if not g.user.is_admin and order.user_id != g.user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Parse service options if they exist
    service_options_html = ""
    if order.service_options:
        options = json.loads(order.service_options)
        service_options_html = "<div class='receipt-section'><h4>Selected Options:</h4>"
        for category, option in options.items():
            service_options_html += f"<div class='receipt-item'><span>{category}:</span><span>{option}</span></div>"
        service_options_html += "</div>"
    
    receipt_data = {
        'order_id': order.id,
        'customer': order.user.name,
        'service_type': order.service_type,
        'quantity': order.quantity,
        'total': order.total,
        'date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'business_name': business_config['businessName'],
        'service_options': service_options_html,
        'requests_comments': order.requests_comments if order.requests_comments else ''
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
        service_options = json.loads(order.service_options) if order.service_options else {}
        return jsonify({
            'id': order.id,
            'service_type': order.service_type,
            'quantity': order.quantity,
            'total': order.total,
            'status': order.status,
            'payment_status': order.payment_status,
            'payment_method': order.payment_method,
            'stripe_payment_intent_id': order.stripe_payment_intent_id,
            'is_subscription_order': order.is_subscription_order,
            'service_options': service_options,
            'requests_comments': order.requests_comments
        })
    
    elif request.method == 'PUT':
        data = request.json
        order.service_type = data.get('service_type', order.service_type)
        order.quantity = data.get('quantity', order.quantity)
        order.total = data.get('total', order.total)
        order.status = data.get('status', order.status)
        order.payment_status = data.get('payment_status', order.payment_status)
        order.payment_method = data.get('payment_method', order.payment_method)
        
        if 'service_options' in data:
            order.service_options = json.dumps(data['service_options'])
        if 'requests_comments' in data:
            order.requests_comments = data['requests_comments']
        
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

@app.route('/api/update-business-config', methods=['POST'])
def update_business_config():
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        new_config = request.json
        config_path = os.environ.get('BUSINESS_CONFIG_PATH', '/app/business_config.json')
        backup_path = f"{config_path}.backup"

        # Enhanced validation
        if not new_config:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['businessName', 'businessDescription', 'about', 'services', 'serviceOptions', 'paymentSettings']
        missing_fields = [field for field in required_fields if field not in new_config]
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Validate payment settings
        payment_settings = new_config.get('paymentSettings', {})
        required_payment_fields = ['acceptCash', 'acceptCard', 'stripeEnabled', 'currency']
        missing_payment_fields = [field for field in required_payment_fields if field not in payment_settings]
        if missing_payment_fields:
            return jsonify({
                'success': False,
                'message': f'Missing payment settings: {", ".join(missing_payment_fields)}'
            }), 400

        # Validate service options structure
        service_options = new_config.get('serviceOptions', {})
        required_option_categories = ['oneTimeOptions', 'subscriptionOptionsAtSignup', 'subscriptionOptionsAtOrder']
        for category in required_option_categories:
            if category not in service_options:
                return jsonify({
                    'success': False,
                    'message': f'Missing service options category: {category}'
                }), 400
            
            # Validate each category's structure
            for option_group in service_options[category]:
                if not isinstance(option_group, dict) or 'categoryName' not in option_group or 'options' not in option_group:
                    return jsonify({
                        'success': False,
                        'message': f'Invalid structure in {category}'
                    }), 400
                
                # Validate options array
                for option in option_group['options']:
                    if not isinstance(option, dict) or 'name' not in option or 'additionalCost' not in option:
                        return jsonify({
                            'success': False,
                            'message': f'Invalid option structure in {category}'
                        }), 400

        # Helper function to generate ID from name
        def generate_id(name):
            return name.lower().replace(' ', '-')

        # Process services and add IDs
        services = new_config.get('services', {})
        if not isinstance(services, dict):
            return jsonify({'success': False, 'message': 'Services must be an object'}), 400

        for service_type in ['oneTime', 'subscription']:
            if service_type not in services:
                return jsonify({'success': False, 'message': f'Missing {service_type} services'}), 400
            
            if not isinstance(services[service_type], list):
                return jsonify({'success': False, 'message': f'{service_type} services must be an array'}), 400

            # Process each service
            for service in services[service_type]:
                required_service_fields = ['name', 'description', 'price']
                if service_type == 'subscription':
                    required_service_fields.extend(['billingFrequency', 'servicesPerPeriod'])

                missing_service_fields = [field for field in required_service_fields if field not in service]
                if missing_service_fields:
                    return jsonify({
                        'success': False,
                        'message': f'Service missing fields: {", ".join(missing_service_fields)}'
                    }), 400

                # Generate and add ID if not present
                if 'id' not in service:
                    service['id'] = generate_id(service['name'])

        # Create/update backup of current config
        if os.path.exists(config_path):
            try:
                shutil.copy2(config_path, backup_path)
            except Exception as e:
                app.logger.warning(f"Failed to create config backup: {str(e)}")

        try:
            # Save the new configuration
            with open(config_path, 'w') as f:
                json.dump(new_config, f, indent=4)
                
            # Update the global business_config
            global business_config
            business_config = new_config

            return jsonify({
                'success': True, 
                'message': 'Configuration updated successfully'
            })

        except Exception as e:
            # If saving failed and we have a backup, restore from backup
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, config_path)
                with open(config_path) as f:
                    business_config = json.load(f)
            raise e

    except Exception as e:
        app.logger.error(f"Failed to update business config: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Failed to update configuration: {str(e)}'
        }), 500

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    if not g.user:
        return jsonify({'error': 'User not authenticated'}), 401

    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    if not stripe_key:
        app.logger.error("Stripe API key not found in environment variables")
        return jsonify({'error': 'Payment service configuration error'}), 500
    
    stripe.api_key = stripe_key

    try:
        data = request.json
        service_type = data.get('serviceType')
        service_id = data.get('serviceId')
        price = data.get('price')
        service_options = data.get('serviceOptions', {})
        requests_comments = data.get('requestsComments', '')

        # Create order with service options
        order_id = str(uuid.uuid4())
        order = Order(
            id=order_id,
            user_id=g.user.id,
            service_type=service_id,
            quantity=1,
            total=float(price),
            payment_method='card',
            payment_status='pending',
            is_subscription_order=(service_type == 'subscription'),
            service_options=json.dumps(service_options),
            requests_comments=requests_comments
        )
        db.session.add(order)

        # Handle subscription creation
        if service_type == 'subscription':
            subscription_config = next(
                (s for s in business_config['services']['subscription'] 
                 if s['id'] == service_id),
                None
            )
            
            if not subscription_config:
                raise ValueError('Invalid subscription service')

            new_subscription = Subscription(
                user_id=g.user.id,
                subscription_id=service_id,
                status='pending',
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                services_allowed=subscription_config['servicesPerPeriod'],
                services_used=0,
                service_options=json.dumps(service_options)
            )
            db.session.add(new_subscription)

        db.session.commit()

        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(float(price) * 100),
            currency=business_config.get('paymentSettings', {}).get('currency', 'usd'),
            metadata={
                'service_type': service_type,
                'service_id': service_id,
                'user_id': g.user.id,
                'order_id': order.id
            }
        )
        
        order.stripe_payment_intent_id = intent.id
        db.session.commit()
        
        return jsonify({
            'clientSecret': intent.client_secret,
            'orderId': order.id
        })

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Payment intent creation failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/submit-order', methods=['POST'])
def submit_order():
    if not g.user:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        data = request.json
        service_type = data.get('serviceType')
        service_id = data.get('serviceId')
        payment_method = data.get('paymentMethod')
        price = data.get('price')
        service_options = data.get('serviceOptions', {})
        requests_comments = data.get('requestsComments', '')

        # Create order with service options
        order = Order(
            id=str(uuid.uuid4()),
            user_id=g.user.id,
            service_type=service_id,
            quantity=1,
            total=float(price),
            payment_method=payment_method,
            payment_status='pending' if payment_method == 'card' else 'unpaid',
            is_subscription_order=(service_type == 'subscription'),
            service_options=json.dumps(service_options),
            requests_comments=requests_comments
        )
        db.session.add(order)
        
        # Handle subscription
        if service_type == 'subscription':
            subscription_config = next(
                (s for s in business_config['services']['subscription'] 
                 if s['id'] == service_id),
                None
            )
            
            if not subscription_config:
                raise ValueError('Invalid subscription service')

            # Create new subscription with signup options
            new_subscription = Subscription(
                user_id=g.user.id,
                subscription_id=service_id,
                status='active',
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                services_allowed=subscription_config['servicesPerPeriod'],
                services_used=0,
                service_options=json.dumps(service_options)  # Save signup options with subscription
            )
            db.session.add(new_subscription)

        db.session.commit()
        return jsonify({
            'success': True,
            'orderId': order.id
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Order submission failed: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Add this helper function for handling successful payments
def handle_successful_payment(payment_intent):
    try:
        # Find the order and update its status
        order = Order.query.filter_by(
            stripe_payment_intent_id=payment_intent.id
        ).first()
        
        if order:
            order.payment_status = 'paid'
            db.session.commit()
            app.logger.info(f"Order {order.id} marked as paid")
            
            # Activate the subscription if it's a subscription order
            if order.is_subscription_order:
                subscription = Subscription.query.filter_by(
                    user_id=order.user_id,
                    subscription_id=order.service_type,
                    status='pending'
                ).first()
                
                if subscription:
                    subscription.status = 'active'
                    db.session.commit()
                    app.logger.info(f"Subscription {subscription.id} activated")
        else:
            app.logger.error(f"Order not found for payment intent {payment_intent.id}")
    except Exception as e:
        app.logger.error(f"Payment success handling failed: {str(e)}")

# Add webhook handler for Stripe events
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_successful_payment(payment_intent)
    
    return jsonify({'received': True})

# Add this new route for marking orders as paid
@app.route('/api/order/<order_id>/mark-paid', methods=['POST'])
def mark_order_paid(order_id):
    if not g.user or not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    order = Order.query.get_or_404(order_id)
    order.payment_status = 'paid'
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    if not g.user:
        flash('Please log in to manage your subscription.', 'warning')
        return redirect(url_for('login'))
    
    try:
        subscription_id = request.form.get('subscription_id')
        if not subscription_id:
            flash('Subscription ID is required.', 'warning')
            return redirect(url_for('profile'))

        # Check if user has this specific subscription
        if not g.user.has_active_subscription_for(subscription_id):
            flash('No active subscription found with this ID.', 'warning')
            return redirect(url_for('profile'))

        # If using Stripe, cancel the subscription in Stripe
        if business_config['paymentSettings'].get('stripeEnabled', False):
            stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
            try:
                # Implement Stripe subscription cancellation here
                pass
            except stripe.error.StripeError as e:
                app.logger.error(f"Stripe subscription cancellation failed: {str(e)}")
                flash('Failed to cancel subscription with payment provider.', 'danger')
                return redirect(url_for('profile'))

        # Cancel the subscription in our database
        if g.user.cancel_subscription(subscription_id):
            # Create a cancellation record in orders
            cancellation_order = Order(
                id=str(uuid.uuid4()),
                user_id=g.user.id,
                service_type=subscription_id,
                quantity=0,
                total=0,
                status='Completed',
                payment_status='not_applicable',
                payment_method='none',
                is_subscription_order=True
            )
            db.session.add(cancellation_order)
            db.session.commit()

            flash('Your subscription has been successfully canceled.', 'success')
        else:
            flash('Failed to cancel subscription. Please try again.', 'danger')

        return redirect(url_for('profile'))

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Subscription cancellation failed: {str(e)}")
        flash('An error occurred while canceling your subscription. Please try again or contact support.', 'danger')
        return redirect(url_for('profile'))

@app.route('/business-config')
def business_config_page():
    # Redirect if not logged in
    if not g.user:
        return redirect(url_for('login'))
    
    # Redirect if not admin
    if not g.user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('business_config.html', business_config=business_config)

@app.route('/subscription-service', methods=['POST'])
def request_subscription_service():
    if not g.user:
        return jsonify({'error': 'User not authenticated'}), 401

    subscription_id = request.form.get('subscription_id')
    if not subscription_id:
        flash('Subscription ID is required.', 'error')
        return redirect(url_for('order_service'))

    # Get the subscription
    subscription = Subscription.query.filter_by(
        user_id=g.user.id,
        subscription_id=subscription_id,
        status='active'
    ).first()

    if not subscription:
        flash('No active subscription found.', 'error')
        return redirect(url_for('order_service'))

    if subscription.services_used >= subscription.services_allowed:
        flash('No services remaining in your subscription.', 'error')
        return redirect(url_for('order_service'))

    try:
        # Collect service options
        service_options = {}
        for category in business_config['serviceOptions']['subscriptionOptionsAtOrder']:
            category_name = category['categoryName']
            option_value = request.form.get(f'option_{category_name}')
            if option_value:
                service_options[category_name] = option_value

        # Get comments
        comments = request.form.get('subscription_comments', '')

        # Create a new order for the service
        order = Order(
            id=str(uuid.uuid4()),
            user_id=g.user.id,
            service_type=subscription_id,
            quantity=1,
            total=0,  # Free since it's part of subscription
            status='Pending',
            payment_status='paid',  # Already paid through subscription
            payment_method='subscription',
            is_subscription_order=True,
            service_options=json.dumps(service_options),
            requests_comments=comments
        )
        
        # Increment the services used count
        subscription.services_used += 1
        
        db.session.add(order)
        db.session.commit()

        flash('Service requested successfully!', 'success')
        return redirect(url_for('order_service'))

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to create subscription service order: {str(e)}")
        flash('Failed to request service. Please try again.', 'error')
        return redirect(url_for('order_service'))

@app.template_filter('from_json')
def from_json(value):
    if not value:
        return {}
    return json.loads(value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
