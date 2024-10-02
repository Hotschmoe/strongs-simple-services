# Simple Service Ordering Web App

A Python-based web application for managing service subscriptions and one-time orders.

## Context

A family member is starting a laundry business and needs a simple web app to manage orders and subscriptions. She wants users to be able to scan a printed QR code on a laundry basket to check out an order. She would also like to be able to view orders and manage subscriptions from a dashboard. This web app needs to be simple to understand and maintain, and cost effective to self host. (so easy to self host that she can do it herself with little to no technical experience).

Users should be able to 1. scan qr code. 2. login if not already logged in. 3. select a service and check out. 4. receive a confirmation and payment receipt. this will then allow her (business owner) to 5. see all orders on a dashboard. 6. check off when orders are completed. and finally 7. be able to print a receipt for each order on demand. Users should also be able to 8. view their profile and 9. edit their profile (name, phone number, address, payment info).

## Features Checklist

- [ ] Docker containerization
  - [ ] Frontend container
  - [ ] Database container
- [ ] User account management
  - [ ] Registration
  - [ ] Login
  - [ ] Profile editing (name, phone number)
- [ ] Stripe integration
  <!-- - [ ] Subscription management -->
  - [ ] One-time service purchases
- [ ] Service ordering page (/order-service)
  - [ ] Standard and rush options
  <!-- - [ ] Subscription status display -->
- [ ] Admin functionality
  - [ ] Database viewing and editing (viewing works, edit button visible but not functional)
  <!-- - [ ] Stripe health monitoring -->
  <!-- - [ ] Settings page -->
- [ ] Environment/config file support
- [ ] Example config file for demo purposes
- [ ] QR code generation page
- [ ] Mobile-first design
- [ ] Stripe activation check and error handling
- [ ] integrate ngrok or similar for easy deployment
- [ ] add a field on ADMIN order page to select user to place an order for

## File Structure

```
simple-service-ordering/
├── app_frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── profile.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   └── register.html
│   ├── Dockerfile.frontend
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
├── docker-compose.yml
├── .dockerignore
├── .gitattributes
├── .gitignore
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
