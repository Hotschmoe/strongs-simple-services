from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # Assume successful login
    return redirect(url_for('order_service'))

@app.route('/order-service')
def order_service():
    services = [
        {
            "title": "Standard",
            "description": "40hr turn around",
            "price": 10
        },
        {
            "title": "Rush",
            "description": "24hr turnaround",
            "price": 20
        }
    ]
    return render_template('order_service.html', services=services)

@app.route('/profile')
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)