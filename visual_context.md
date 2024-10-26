# Technology Stack

## Backend
- Python with Flask framework

## Database
- SQLite with SQLAlchemy ORM

## Frontend
- HTML templates with Bootstrap for styling

## Containerization
- Docker for easy deployment

## Additional Services
- ngrok for public access during development

```mermaid
graph TD
    A[User] -->|Accesses| B[Web Browser]
    B -->|Sends HTTP Request| C[Flask Web Application]
    C -->|Renders| D[HTML Templates]
    D -->|Displays| B
    C -->|Interacts with| E[SQLite Database]
    C -->|Generates| F[QR Code]
    G[Admin] -->|Manages| C
    C -->|Uses| H[business_config.json]

    subgraph "Flask Web Application"
    I[User Management]
    J[Order Processing]
    K[Admin Dashboard]
    L[QR Code Generation]
    end

    subgraph "Database"
    M[Users Table]
    N[Orders Table]
    end

    C --> I
    C --> J
    C --> K
    C --> L
    E --> M
    E --> N
```