from flask import Flask, render_template, g, redirect, url_for, request, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

class User:
    def __init__(self, is_authenticated=False, name="", phone="", address=""):
        self.is_authenticated = is_authenticated
        self.name = name
        self.phone = phone
        self.address = address

@app.before_request
def before_request():
    if 'user' not in session:
        session['user'] = {'is_authenticated': False, 'name': '', 'phone': '', 'address': ''}
    g.user = User(**session['user'])

@app.route('/')
def index():
    if not g.user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html', user=g.user)

@app.route('/order')
def order():
    return render_template('order.html', user=g.user)

@app.route('/profile')
def profile():
    # For demonstration, let's create a user with some data
    g.user = User(is_authenticated=True, name="John Doe", phone="123-456-7890", address="123 Main St, Anytown, USA")
    return render_template('profile.html', user=g.user)

@app.route('/dashboard')
def dashboard():
    # Placeholder data for orders
    orders = [
        {"id": 1, "customer_name": "Alice", "service_type": "Standard Wash", "status": "Pending"},
        {"id": 2, "customer_name": "Bob", "service_type": "Rush Wash", "status": "Completed"},
    ]
    settings = {"business_name": "My Laundry Service", "stripe_key": "pk_test_..."}
    return render_template('dashboard.html', user=g.user, orders=orders, settings=settings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Always set the user as authenticated for now
        session['user'] = {'is_authenticated': True, 'name': 'John Doe', 'phone': '123-456-7890', 'address': '123 Main St, Anytown, USA'}
        print("User authenticated, redirecting to index")  # Debug print
        return redirect(url_for('index'))
    return render_template('login.html', user=g.user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Here you would typically create a new user account
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', user=g.user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)