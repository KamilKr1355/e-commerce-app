# Cardsino - E-commerce Backend API

A modular e-commerce API integrated with Stripe (Payments) and Furgonetka (Logistics).  
Designed for scalability with features like guest checkout, transaction-safe inventory management, and automated background tasks.

## Quick Start

**Requirements:** Docker  
**Environment:** Create a `.env` file in the root directory

### Run

```bash
docker-compose up --build
```
Swagger Docs

Swagger UI at http://localhost:8000/docs

### .env
```bash
DATABASE_URL	Database connection string
SECRET_KEY / ALGORITHM	JWT signing key and algorithm for Authentication
sk_stripe / STRIPE_WEBHOOK_SECRET	Stripe API Secret and Webhook Signing Secret
FURGONETKA_...	API credentials for shipping services and point maps:
• FURGONETKA_CLIENT_ID
• FURGONETKA_CLIENT_SECRET
• FURGONETKA_USERNAME
• FURGONETKA_PASSWORD
• FURGONETKA_WEBHOOK_SALT
SMTP_...	SMTP server credentials:
• SMTP_SERVER
• SMTP_PORT
• SMTP_USER
• SMTP_PASS
ADMIN_EMAIL / ADMIN_PASSWORD	Credentials for the SuperAdmin account (auto-created on startup)
```
### Backend Structure
```bash
src/
├── admin/       # Sales statistics and admin dashboard logic
├── auth/        # Authentication, JWT, and password hashing
├── products/    # Product, category, and image management
├── shopping/    # Cart logic and order processing (User & Guest)
├── logistics/   # Stripe integration and shipment models
├── furgonetka/  # Courier integration (Webhooks, status tracking, maps)
├── email/       # SMTP email service for notifications
└── main.py      # Application entry point, CORS, and periodic tasks
```
