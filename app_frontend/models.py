from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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
    
    # New subscription fields
    stripe_customer_id = db.Column(db.String(120), unique=True, nullable=True)
    subscription_status = db.Column(db.String(20), default='none')  # none, active, canceled, expired
    subscription_start_date = db.Column(db.DateTime, nullable=True)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    subscription_type = db.Column(db.String(50), nullable=True)
    services_allowed = db.Column(db.Integer, default=0)
    services_used = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def has_active_subscription(self):
        return (self.subscription_status == 'active' and 
                self.subscription_end_date and 
                self.subscription_end_date > datetime.utcnow())

    def get_remaining_services(self):
        if not self.has_active_subscription():
            return 0
        return max(0, self.services_allowed - self.services_used)

    def cancel_subscription(self):
        """
        Cancels the user's subscription and updates relevant fields
        """
        self.subscription_status = 'canceled'
        self.subscription_end_date = datetime.utcnow()
        
    def can_cancel_subscription(self):
        """
        Checks if the user can cancel their subscription
        """
        return self.has_active_subscription() and self.subscription_status not in ['canceled', 'pending_cancellation']

class Order(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(20), nullable=True)
    stripe_payment_intent_id = db.Column(db.String(120), nullable=True)
    is_subscription_order = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
