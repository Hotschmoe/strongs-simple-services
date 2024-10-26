# Simple Service Ordering Web App

A Python-based web application for managing service subscriptions and one-time orders.

## Context

A family member is starting a laundry business and needs a simple web app to manage orders and subscriptions. She wants users to be able to scan a printed QR code on a laundry basket to check out an order. She would also like to be able to view orders and manage subscriptions from a dashboard. This web app needs to be simple to understand and maintain, and cost effective to self host. (so easy to self host that she can do it herself with little to no technical experience).

Users should be able to 1. scan qr code. 2. login if not already logged in. 3. select a service and check out. 4. receive a confirmation and payment receipt. this will then allow her (business owner) to 5. see all orders on a dashboard. 6. check off when orders are completed. and finally 7. be able to print a receipt for each order on demand. Users should also be able to 8. view their profile and 9. edit their profile (name, phone number, address, payment info).

## Features Checklist

- [x] Docker containerization
  - [x] Frontend container
  - [x] Database - SQLite
- [x] User account management
  - [x] Registration
  - [x] Login
  - [x] Profile editing (name, phone number)
- [ ] Stripe integration
  <!-- - [ ] Subscription management -->
  - [ ] One-time service purchases
- [x] Service ordering page
  - [x] Standard and rush options
  <!-- - [ ] Subscription status display -->
- [ ] Admin functionality
  - [x] Database viewing and editing (viewing works, editing functional)
  - [ ] Implement form-based interface for easier database editing
  <!-- - [ ] Stripe health monitoring -->
  <!-- - [ ] Settings page -->
- [x] QR code generation page
- [x] Mobile-first design
<!-- - [ ] Stripe activation check and error handling -->
- [ ] add a field on ADMIN order page to select user to place an order for
- [ ] at some point we'll want to incorporate stripe for online payments
- [x] when we feel good, we'll make a config file so any service provider can use this by entering their business name, description and a json of services that will populate the ordering field
- [x] Integrate ngrok for easy public access

## File Structure

```
simple-service-ordering/
├── app_frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── profile.html
│   │   ├── qr_code.html
│   │   └── register.html
│   ├── Dockerfile.frontend
│   ├── business_config.json
│   ├── database.py
│   ├── extensions.py
│   ├── main.py
│   ├── models.py
│   └── requirements.txt
├── docker-compose.yml
├── .dockerignore
├── .gitattributes
├── .gitignore
└── README.md
```

## Setup

1. Clone the repository
2. Make sure you have Docker and Docker Compose installed on your system
3. Create a `.env` file in the root directory with the following content:
   ```
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=adminpassword
   ADMIN_NAME=Admin User
   ADMIN_PHONE=1234567890
   ADMIN_ADDRESS=123 Admin St, Admin City
   NGROK_AUTH_TOKEN=your_ngrok_auth_token
   ```
4. Sign up for a free ngrok account at https://ngrok.com/ and get your auth token
5. Replace `your_ngrok_auth_token` in the `.env` file with your actual ngrok auth token
6. Build and run Docker containers:
   ```
   docker-compose up --build
   ```
7. Access the web app locally at `http://localhost:5000`
8. To access the public URL:
   - Open `http://localhost:4040` in your browser
   - Look for the "Forwarding" URL (e.g., `https://abcd1234.ngrok.io`)
   - Use this URL to access your web app from anywhere

## Development

To run the app in development mode:

1. Follow the setup instructions above
2. Make changes to the code as needed
3. The app will automatically reload when changes are detected

## Deployment and Public Access

For production deployment:

1. Update the `docker-compose.yml` file to use production settings
2. Set up a reverse proxy (e.g., Nginx) to handle HTTPS
3. Use a production-ready database (e.g., PostgreSQL) instead of SQLite
4. Set up proper logging and monitoring

### Public Access Options

To make your web app accessible from the internet, you have several options:

1. **Port Forwarding**: Configure your router to forward incoming traffic on a specific port to your local machine. This is suitable for simple setups but may have security implications.

2. **Reverse Proxy**: Set up a reverse proxy server (like Nginx or Traefik) on a publicly accessible server. This provides more control and security features.

3. **ngrok (for development/testing)**: We've included a commented-out ngrok service in the `docker-compose.yml` file for easy setup during development or testing. To use it:

   a. Uncomment the ngrok service in `docker-compose.yml`
   b. Add your ngrok auth token to the `.env` file:
      ```
      NGROK_AUTHTOKEN=your_ngrok_auth_token
      ```
   c. Run `docker-compose up` to start the services
   d. Access the ngrok interface at `http://localhost:4040` to find your public URL

   Note: ngrok is not recommended for production use due to its temporary nature and potential security concerns.

For production environments, we recommend using a reverse proxy with proper HTTPS configuration. This provides better security, performance, and control over your deployment.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your fork
5. Submit a pull request

## License

This project is licensed under the MIT License.