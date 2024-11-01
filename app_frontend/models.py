from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    orders = db.relationship('Order', backref='user', lazy=True)
    is_subscriber = db.Column(db.Boolean, default=False)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class SubscriptionUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    services_allowed = db.Column(db.Integer, nullable=False)
    services_used = db.Column(db.Integer, default=0)
    
class Order(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_type = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    is_subscription = db.Column(db.Boolean, default=False)
    subscription_period = db.Column(db.String(20), nullable=True)
    subscription_start_date = db.Column(db.DateTime, nullable=True)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    services_per_period = db.Column(db.Integer, nullable=True)
    subscription_usage = db.relationship('SubscriptionUsage', backref='order', lazy=True)
