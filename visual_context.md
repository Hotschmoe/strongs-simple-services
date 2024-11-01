# Technology Stack

## Backend
- Python with Flask framework
- Stripe integration for payments (Payment Intents only)

## Database
- SQLite with SQLAlchemy ORM
- Automatic schema updates and backups

## Frontend
- HTML templates with Bootstrap for styling
- Stripe Elements for payment forms

## Containerization
- Docker for easy deployment

## Additional Services
- ngrok for public access during development

## Key Features

### User Flow
1. User registers/logs in
2. Browses services (one-time or subscription)
3. Selects service and payment method
4. Completes payment (cash or card)
5. Receives order confirmation

### Subscription Flow
1. User selects subscription plan
2. Completes initial payment
3. System tracks service usage
4. Automatic renewal process
5. Cancellation handling

### Admin Flow
1. Manages orders and subscriptions
2. Updates business configuration
3. Monitors payments
4. Generates QR codes
5. Manages database

### Payment Processing
1. Simple Stripe integration using Payment Intents
2. No Stripe Products/Price IDs
3. Pricing managed in business_config.json
4. Support for both one-time and subscription payments

```mermaid
graph TD
    A[User] -->|Accesses| B[Web Browser]
    B -->|Sends HTTP Request| C[Flask Web Application]
    C -->|Renders| D[HTML Templates]
    D -->|Displays| B
    C -->|Interacts with| E[SQLite Database]
    C -->|Generates| F[QR Code]
    C -->|Processes Payments| G[Stripe API]
    H[Admin] -->|Manages| C
    C -->|Uses| I[business_config.json]

    subgraph "Flask Web Application"
    J[User Management]
    K[Order Processing]
    L[Payment Processing]
    M[Subscription Management]
    N[Admin Dashboard]
    O[QR Code Generation]
    end

    subgraph "Database"
    P[Users Table]
    Q[Orders Table]
    R[Subscriptions]
    end

    subgraph "Payment Flow"
    S[Create Payment Intent]
    T[Process Payment]
    U[Update Order Status]
    end

    C --> J
    C --> K
    C --> L
    C --> M
    C --> N
    C --> O
    E --> P
    E --> Q
    E --> R
    L --> S
    S --> T
    T --> U
```