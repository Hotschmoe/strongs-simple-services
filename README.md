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
- [x] when we feel good, we'll make a config file so any service provider can use this by entering their business name, description and a json of services that will populate the ordering field
- [x] Integrate ngrok for easy public access

- [ ] Make subscription based services in config file as option
- [ ] Pay one-time order with stripe
- [ ] Pay subscription with stripe
- [ ] subscription status display on dashboard - admin
- [ ] subscription management on profile page - user
- [ ] User to order service (e.g. wash pickup) if subscription is active (show remaining service count for month)
- [ ] About biz page - config in business_config.json - simple text, contact, possibly image and links to social media
- [ ] DASHBOARD - make edit more formlike
- [ ] move business config to database? (with default values to init database)
- [ ] update readme to reflect current status
- [ ] update readme to show how to use static directory for favicon and images
- [ ] add image option to services under business_config.json that links to static directory - force image size? (e.g. 100x100)

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

## Database Management

The application includes built-in database management features accessible to admin users from the dashboard:

### Backup and Restore
- **Backup**: Create a timestamped backup of the current database
- **Backup & Download**: Create and download a backup file
- **Restore**: Upload and restore a previous backup file

### Database Migrations
When the application's database structure needs to be updated (e.g., adding new fields or tables), the system uses Flask-Migrate (Alembic) to handle migrations safely.

#### For Developers
To create a new migration after modifying models:

1. Make your changes to the models in `models.py`

2. Access the Docker container:
   ```bash
   # First, find your container ID
   docker ps
   
   # Access the container (replace CONTAINER_ID with your frontend container ID)
   docker exec -it CONTAINER_ID bash
   
   # Alternatively, you can use the service name from docker-compose
   docker exec -it services_frontend bash
   ```

3. Once inside the container, generate the migration:
   ```bash
   # Initialize migrations (only needed the first time)
   flask db init
   
   # Create a new migration
   flask db migrate -m "Description of changes"
   ```

4. The migration files will be created in the `migrations/versions/` directory of your project
   - These files are automatically mapped to your local directory through Docker volumes
   - Review the generated migration file to ensure the changes are correct
   - Commit these files to your repository

#### For Administrators
When database structure updates are available:

1. **Always backup first**: Use the "Backup & Download" button on the dashboard to create a safe backup
2. Click the "Run Database Migration" button on the dashboard
3. The system will:
   - Create an automatic backup
   - Apply all pending migrations
   - Display the migration results
   - Reload the page to reflect changes

#### Migration Safety Features
- Automatic backup creation before migration
- Version tracking
- Admin-only access
- Confirmation dialog to prevent accidental migrations
- Clear feedback about the migration process

### Troubleshooting

If you encounter issues during migration:

1. Check the application logs:
   ```bash
   # View container logs
   docker logs services_frontend
   
   # Or follow the logs in real-time
   docker logs -f services_frontend
   ```

2. If needed, restore a backup using the dashboard's restore function

3. For more detailed investigation, you can access the container:
   ```bash
   docker exec -it services_frontend bash
   
   # Once inside, you can check the current migration status
   flask db current
   
   # Or view migration history
   flask db history
   ```

4. Contact technical support with the error details and logs

Note: It's recommended to test migrations in a development environment before applying them to production. You can create a development environment by:
1. Making a copy of your production database
2. Running the application in a separate Docker container
3. Testing the migration process
4. Only after successful testing, apply the migration to production

### Common Migration Commands
When inside the Docker container, you can use these Flask-Migrate commands:

```bash
flask db init          # Initialize migrations (first time only)
flask db migrate       # Generate a new migration
flask db upgrade      # Apply migrations
flask db downgrade    # Rollback the last migration
flask db current      # Show current migration version
flask db history      # Show migration history
flask db show        # Show the current migration
```