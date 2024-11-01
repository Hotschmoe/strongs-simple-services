from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.String(50), nullable=False)  # matches the id in business_config.json
    status = db.Column(db.String(20), default='active')  # active, canceled, expired
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    services_allowed = db.Column(db.Integer, nullable=False)
    services_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

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
    
    # Add relationship to subscriptions
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_active_subscriptions(self):
        """Returns a list of active subscription details"""
        now = datetime.utcnow()
        active_subs = []
        for sub in self.subscriptions:
            if (sub.status == 'active' and 
                sub.end_date and 
                sub.end_date > now):
                active_subs.append({
                    'id': sub.subscription_id,
                    'remaining_services': max(0, sub.services_allowed - sub.services_used),
                    'end_date': sub.end_date
                })
        return active_subs

    def has_active_subscription_for(self, subscription_id):
        """Check if user has an active subscription for a specific plan"""
        now = datetime.utcnow()
        return any(
            sub.subscription_id == subscription_id and
            sub.status == 'active' and 
            sub.end_date and 
            sub.end_date > now 
            for sub in self.subscriptions
        )

    def get_subscription(self, subscription_id):
        """Get a specific subscription by its ID"""
        return next(
            (sub for sub in self.subscriptions 
             if sub.subscription_id == subscription_id and 
             sub.status == 'active'), 
            None
        )

    def get_remaining_services(self, subscription_id=None):
        """
        Get remaining services for a specific subscription or total across all active subscriptions
        """
        if subscription_id:
            subscription = self.get_subscription(subscription_id)
            if not subscription or subscription.status != 'active':
                return 0
            return max(0, subscription.services_allowed - subscription.services_used)
        
        # If no subscription_id provided, sum all active subscriptions
        return sum(
            max(0, sub.services_allowed - sub.services_used)
            for sub in self.subscriptions
            if sub.status == 'active' and sub.end_date > datetime.utcnow()
        )

    def cancel_subscription(self, subscription_id):
        """Cancels a specific subscription"""
        subscription = self.get_subscription(subscription_id)
        if subscription and subscription.status == 'active':
            subscription.status = 'canceled'
            subscription.end_date = datetime.utcnow()
            return True
        return False

    def can_cancel_subscription(self, subscription_id):
        """Checks if a specific subscription can be canceled"""
        subscription = self.get_subscription(subscription_id)
        return (subscription and 
                subscription.status == 'active' and 
                subscription.end_date > datetime.utcnow())

    def has_active_subscription(self):
        """Check if user has any active subscription"""
        now = datetime.utcnow()
        return any(
            sub.status == 'active' and 
            sub.end_date and 
            sub.end_date > now 
            for sub in self.subscriptions
        )

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
