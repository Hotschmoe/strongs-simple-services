from flask import Flask, render_template, g, redirect, url_for, request, flash, session, jsonify
import uuid
from database import init_db
from extensions import db
from models import User, Order
import qrcode
import io
import base64

app = Flask(__name__)
init_db(app)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            g.user = user

@app.route('/')
def index():
    if not g.user:
        flash('Please log in to place an order.', 'warning')
        return redirect(url_for('login'))
    return render_template('index.html', user=g.user)

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

    return render_template('profile.html', user=g.user)

@app.route('/dashboard')
def dashboard():
    if not g.user or not g.user.is_admin:
        flash('You do not have permission to access the dashboard.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    orders = Order.query.join(User).all()
    return render_template('dashboard.html', users=users, orders=orders)

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
    return render_template('login.html', user=g.user)

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
    return render_template('register.html', user=g.user)

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
    order_url = f"{current_domain}/"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(order_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('qr_code.html', qr_code=img_str)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)