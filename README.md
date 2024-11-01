# Simple Service Ordering Web App

A Python-based web application for managing service subscriptions and one-time orders, with integrated payment processing.

## Context

This web application helps service-based businesses manage orders and subscriptions. Key features include:
- QR code-based ordering system
- User account management
- Subscription and one-time service ordering
- Stripe payment integration
- Admin dashboard for business management
- Easy self-hosting capabilities

## Features

### Implemented
- [x] Docker containerization
  - [x] Frontend container
  - [x] SQLite database with automatic schema updates
- [x] User account management
  - [x] Registration
  - [x] Login
  - [x] Profile editing (name, phone, address)
- [x] Service ordering system
  - [x] One-time services
  - [x] Subscription services
  - [x] QR code generation for easy ordering
- [x] Admin functionality
  - [x] Order management
  - [x] User management
  - [x] Business configuration editor
  - [x] Database backup and restore
- [x] Payment processing
  - [x] Stripe integration for card payments
  - [x] Cash payment tracking
- [x] Mobile-first responsive design
- [x] Business configuration via JSON
- [x] Development access via ngrok

### In Progress
- [ ] Subscription management
  - [ ] Automatic renewal processing
  - [ ] Usage tracking
  - [ ] Cancellation handling
- [ ] Enhanced admin dashboard
  - [ ] Form-based interface for database editing
  - [ ] Improved order management UI
- [ ] Business customization
  - [ ] Static directory for favicon and images
  - [ ] Service images in business_config.json
  - [ ] About page configuration
- [ ] User interface improvements
  - [ ] Footer with business information and social media links
  - [ ] Contact owner button/information on user profile page

## Payment Processing

### Stripe Integration Philosophy
We maintain a simplified Stripe implementation that:
- Uses Payment Intents for direct payment processing
- Avoids Stripe Products and Price IDs
- Manages product/service definitions locally in business_config.json
- Handles pricing and subscription logic within the application

This approach provides:
- Simpler maintenance and configuration
- Direct control over pricing and products
- Easier customization for business owners
- Reduced dependency on Stripe's product ecosystem

### Supported Payment Features
- [x] One-time payments via Stripe
- [x] Subscription payments
- [x] Cash payment tracking
- [x] Payment status monitoring
- [ ] Automatic subscription renewal
- [ ] Subscription cancellation handling

### Refunds
Refunds must be processed directly through the Stripe dashboard. This application does not support initiating refunds through the web interface. For more information on processing refunds, please refer to the [Stripe documentation](https://stripe.com/docs/refunds).

## Setup

### Prerequisites
- Docker and Docker Compose
- Stripe account (for payment processing)
- ngrok account (for development/testing)

### Configuration

1. Clone the repository
2. Create a `.env` file with the following variables:

```
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=adminpassword
ADMIN_NAME=Admin User
ADMIN_PHONE=1234567890
ADMIN_ADDRESS=123 Admin St
NGROK_AUTH_TOKEN=your_ngrok_auth_token
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

### Business Configuration

Edit `app_frontend/business_config.json` to customize:
- Business information
- Service offerings
- Pricing
- Subscription plans

Example configuration:

```json
{
    "businessName": "Fresh & Clean Laundry",
    "businessDescription": "Professional laundry and wash services",
    "about": "Fresh & Clean Laundry provides convenient and reliable laundry services. We handle your clothes with care and ensure they come back clean, fresh, and neatly folded.",
    "paymentSettings": {
        "acceptCash": true,
        "acceptCard": true,
        "stripeEnabled": true,
        "currency": "usd"
    },
    "services": {
        "oneTime": [
            {
                "name": "Standard Loads",
                "description": "Pickup, Wash, Fold.",
                "price": 25
            },
            {
                "name": "Rush Loads",
                "description": "Pickup, Wash, Fold. in 48 hours",
                "price": 35
            }
        ],
        "subscription": [
            {
                "name": "Standard Wash Plan",
                "description": "4 washes per month",
                "price": 80,
                "billingFrequency": "monthly",
                "servicesPerPeriod": 4
            },
            {
                "name": "Large Wash Plan",
                "description": "6 washes per month",
                "price": 90,
                "billingFrequency": "monthly",
                "servicesPerPeriod": 6
            }
        ]
    }
}
```

### Deployment

#### Development
1. Run `docker-compose up --build`
2. Access locally at `http://localhost:5000`
3. For public access, enable ngrok service in docker-compose.yml

#### Production
1. Update docker-compose.yml for production settings
2. Configure a reverse proxy (nginx recommended)
3. Set up SSL certificates
4. Configure proper logging
5. Consider switching to PostgreSQL for database

## Database Management

The application includes built-in database management features:
- Automatic schema updates
- Backup creation and restoration
- Data migration handling

## Contributing

See the contributing guidelines in the repository. Key areas for contribution:
1. Subscription management improvements
2. Admin interface enhancements
3. Documentation updates
4. Test coverage
5. Security improvements

## License

This project is licensed under the MIT License.
