# BNPL (Buy Now Pay Later) System

A Django-based backend system for managing installment payment plans with merchant and user interfaces.

## Features

### Core Features
- **Merchant Features**
  - Create BNPL payment plans with custom parameters
  - View all created payment plans
  - Automatic installment generation (equal monthly payments)
  
- **User Features**
  - View assigned payment plans
  - View installment details and payment status
  - Simulate installment payments
  - Dashboard with payment progress

- **System Features**
  - Automatic status updates (Completed when all installments paid)
  - Overdue installment marking (via scheduled tasks)
  - Payment progress tracking
  - Secure API endpoints with JWT authentication

### Technical Features
- RESTful API with DRF
- JWT Authentication
- Automated status transitions
- Scheduled overdue checks
- Comprehensive test coverage
- Dockerized development environment
- PostgreSQL database

## Installation

### Prerequisites
- Python 3.9+
- Docker (optional)
- PostgreSQL

### Setup
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/bnpl-system.git
   cd bnpl-system
   ```
2. Activate your venv using
   ```bash python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    venv\Scripts\activate  # Windows
   ```
   OR
    if you use docker 
    ```bash 
   docker-compose up --build
    ```

3. Run db_seed.py "optional"
   ```bash python -m venv venv
    docker compose run backend python3 seed_db.py
   ```

4. To run the unit tests
   ```bash python -m venv venv
    docker compose run backend pytest payments/ users/
   ```
   

## security considerations

1. Use rate limiter in your api
2. Isolate your pay services inside a vpc and close all the ports
3. Communicate with your pay service using proxy server
4. Use lambda function as webhooks to update your payment status instead of hooks
5. Separate payment service from user service
6. Do regular stress and penetration tests on your services
7. Field level encryption for sensitive data
8. Validate parameters "use pydantic"
9. Audit logging
10. Use firewalls in your servers
11. Use Secret management services


## Bonus points "TODO"
If I had the time I'd have implemented:
   1. mark as late it can be done using either cronjob+django commands or celery beat
   2. The second point can be easily done using a celery task that check if the payment is within 2 days then send a notification to the user
   and the notification can be integrated with other third party like CEQUENS or sendgrid

## Tradeoffs
1. simplified data validation due to time constraints
2. sacrifice bonus points to start working on frontend
3. didn't implement any logs or monitoring tool due to time constraints
4. used docker compose to simplify development process
5. allowed all cors due to e2e tests with frontend
6. doesn't handle high concurrency for now due to time constraints and evolutionary design principles