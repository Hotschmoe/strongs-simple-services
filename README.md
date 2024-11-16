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
  - [ ] Automatic database backups
  - [ ] PostgreSQL support for production
- [x] User account management
  - [x] Registration
  - [x] Login
  - [x] Profile editing (name, phone, address)
  - [x] Admin user management
  - [ ] Password reset functionality
  - [ ] Email verification
- [x] Service ordering system
  - [x] One-time services
  - [x] Subscription services
  - [x] QR code generation for easy ordering
  - [x] Service options and add-ons
  - [ ] Order history and tracking
  - [ ] Service availability scheduling
- [x] Admin functionality
  - [x] Order management
  - [x] User management
  - [x] Business configuration editor
  - [x] Database backup and restore
  - [ ] Analytics dashboard
  - [ ] Bulk operations (orders/users)
  - [ ] Email notifications
  - [ ] SMS notifications
  - [ ] Calendar integration
  - [ ] Proxy-ordering (admin can order for users)
  - [ ] Handle payment failures
  - [ ] Handle subscription turnover (cancel/renew/consumed)
  - [ ] Handle Consent Forms and Agreement Signatures (save to database)
  - [ ] Migration and database on updates
- [x] Payment processing
  - [x] Stripe integration for card payments
  - [x] Cash payment tracking
  - [x] Payment status monitoring
  - [ ] Multiple payment gateway support
  - [ ] Partial refund handling
- [x] Mobile-first responsive design
- [x] Business configuration via JSON
- [x] Development access via ngrok

### In Progress
- [ ] Subscription management
  - [ ] Automatic renewal processing
  - [ ] Usage tracking and limits
  - [ ] Cancellation handling
  - [ ] Plan switching
  - [ ] Prorated billing
  - [ ] Subscription pause/resume
- [ ] Enhanced admin dashboard
  - [ ] Form-based interface for database editing
  - [ ] Improved order management UI
  - [ ] Customer communication system
  - [ ] Staff management and permissions
  - [ ] Audit logging
- [ ] Business customization
  - [ ] Static directory for favicon and images
  - [ ] Service images in business_config.json
  - [ ] About page configuration
  - [ ] Custom CSS themes
  - [ ] Email template customization
- [ ] User interface improvements
  - [ ] Footer with business information and social media links
  - [ ] Contact owner button/information on user profile page
  - [ ] Dark mode toggle
  - [ ] Accessibility improvements
  - [ ] Mobile app-like experience

### Future Features
- [ ] Advanced Business Features
  - [ ] Multi-location support
  - [ ] Inventory management
  - [ ] Employee scheduling
  - [ ] Customer loyalty program
  - [ ] Gift cards and promotions
- [ ] Integration Capabilities
  - [ ] SMS notifications
  - [ ] Email marketing integration
  - [ ] Calendar integration (Google, iCal)
  - [ ] Accounting software integration
  - [ ] Social media integration
- [ ] Enhanced Security
  - [ ] Two-factor authentication
  - [ ] API key management
  - [ ] Rate limiting
  - [ ] Enhanced audit logging
  - [ ] GDPR compliance tools
- [ ] Reporting and Analytics
  - [ ] Sales reports
  - [ ] Customer analytics
  - [ ] Service popularity metrics
  - [ ] Revenue forecasting
  - [ ] Custom report builder
- [ ] Customer Experience
  - [ ] Customer portal
  - [ ] Mobile app
  - [ ] Service ratings and reviews
  - [ ] Automated customer support
  - [ ] Appointment scheduling

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
                "price": 25,
                "id": "standard-loads"
            },
            {
                "name": "Rush Loads",
                "description": "Pickup, Wash, Fold. in 48 hours",
                "price": 35,
                "id": "rush-loads"
            }
        ],
        "subscription": [
            {
                "name": "Standard Wash Plan",
                "description": "4 washes per month",
                "price": 80,
                "billingFrequency": "monthly",
                "servicesPerPeriod": 4,
                "id": "standard-wash-plan"
            }
        ]
    },
    "serviceOptions": {
        "categories": [
            {
                "categoryName": "Detergents",
                "options": [
                    {
                        "name": "EOS Hypoallergenic Liquid Laundry Detergent + Enzymes - Lavender Scent",
                        "additionalCost": 0
                    },
                    {
                        "name": "Persil OXI + Odor Power Liquid Laundry Detergent",
                        "additionalCost": 0
                    },
                    {
                        "name": "Molly Suds Laundry Powder - Unscented",
                        "additionalCost": 1
                    }
                ]
            },
            {
                "categoryName": "Stain Removers",
                "options": [
                    {
                        "name": "None",
                        "additionalCost": 0
                    },
                    {
                        "name": "Oxy Clean",
                        "additionalCost": 1
                    },
                    {
                        "name": "Shout",
                        "additionalCost": 1
                    }
                ]
            },
            {
                "categoryName": "Drying",
                "options": [
                    {
                        "name": "None",
                        "additionalCost": 0
                    },
                    {
                        "name": "Bounce Dryer Sheets - Outdoor Fresh",
                        "additionalCost": 0
                    },
                    {
                        "name": "Wool Dryer Balls - No Scent",
                        "additionalCost": 0
                    }
                ]
            }
        ],
        "requestsComments": ""
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
