# Simple Service Ordering Web App

A Python-based web application for managing service subscriptions and one-time orders.

## Features Checklist

- [ ] Python-based backend
- [ ] Docker containerization
  - [ ] Frontend container
  - [ ] Database container
- [ ] User account management
  - [ ] Registration
  - [ ] Login
  - [ ] Profile editing (name, phone number)
- [ ] Stripe integration
  - [ ] Subscription management
  - [ ] One-time service purchases
- [ ] QR code scanning for service ordering
- [ ] Service ordering page (/order-service)
  - [ ] Standard and rush options
  - [ ] Subscription status display
- [ ] Admin functionality
  - [ ] Database viewing and editing
  - [ ] Stripe health monitoring
  - [ ] Settings page
- [ ] Environment/config file support
- [ ] Example config file for demo purposes
- [ ] QR code generation page
- [ ] Mobile-first design
- [ ] Stripe activation check and error handling


mkdir docker app app\models app\routes app\services app\templates app\templates\admin app\static app\static\css app\static\js tests

## File Structure

```
simple-service-ordering/
├── docker/
│ ├── Dockerfile.frontend
│ └── Dockerfile.database
├── app/
│ ├── main.py
│ ├── config.py
│ ├── models/
│ │ ├── init.py
│ │ ├── user.py
│ │ └── order.py
│ ├── routes/
│ │ ├── init.py
│ │ ├── auth.py
│ │ ├── order.py
│ │ └── admin.py
│ ├── services/
│ │ ├── init.py
│ │ ├── stripe_service.py
│ │ └── qr_code_service.py
│ ├── templates/
│ │ ├── base.html
│ │ ├── login.html
│ │ ├── register.html
│ │ ├── profile.html
│ │ ├── order_service.html
│ │ └── admin/
│ │ ├── dashboard.html
│ │ └── settings.html
│ └── static/
│ ├── css/
│ │ └── styles.css
│ └── js/
│ └── main.js
├── tests/
│ ├── init.py
│ ├── test_auth.py
│ └── test_order.py
├── .env.example
├── config.yaml.example
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository
2. Copy the example config file and adjust as needed
3. Build and run Docker containers
4. Access the web app at the specified URL

## Development

[Add development instructions here]

## Deployment

[Add deployment instructions here]

## Contributing

[Add contribution guidelines here]

## License

[Add license information here]
