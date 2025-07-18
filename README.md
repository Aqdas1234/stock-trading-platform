# 📈 Stock Trading Platform 

## 🚀 Project Overview

A scalable and performant backend system for a stock trading platform, built using Django REST Framework.
The system supports user registration, real-time stock data management, transaction processing, and robust account validation.
It is built with modern backend architecture, containerization, caching, and asynchronous processing.

---


## 🏗️ System Architecture

The platform is composed of the following components:

- **Django REST Framework** – Core backend API logic
- **PostgreSQL** – Relational database for persistent data
- **Redis** – Caching layer and Celery broker
- **Celery** – For async transaction processing
- **Flower** – Monitoring Celery tasks
- **JWT Auth** – For secure access control
- **Docker Compose** – For easy orchestration of services



---

## ⚙️ Setup Instructions

🛠️ Environment Variables Setup
You need to create a .env file in the project where manage.py file exist with the following environment variable names:

```bash
SECRET_KEY=
DEBUG=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DATABASE_URL=
```
🔐 Note: Fill in the actual values as per your local or production environment.

### 📌 Local Setup

```bash

# Clone the repository
git clone https://github.com/aqdas1234/stock-trading-platform.git
cd stock_trading


# Create virtual environment (Poetry manages this internally)
poetry install

# Activate virtual environment (only needed for manual run)
poetry shell

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver

# Build and run all containers (make sure Dockerfile uses Poetry)
docker compose up --build

# To access the Django server
http://localhost:8000

# To access Flower (Celery monitoring)
http://localhost:5555/

```
