# Setup Guide

This guide will help you set up the Crossborder Luxury E-commerce Platform on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+**: [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 15+**: [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis 7+**: [Download Redis](https://redis.io/download)
- **Git**: [Download Git](https://git-scm.com/downloads)

### Optional (for Docker setup)
- **Docker**: [Download Docker](https://www.docker.com/get-started)
- **Docker Compose**: Usually included with Docker Desktop

## Setup Options

### Option 1: Docker Setup (Recommended for Quick Start)

1. **Clone the repository**
```bash
git clone https://github.com/MIraITwowa/crossborder.git
cd crossborder
```

2. **Build and start all services**
```bash
docker-compose up --build
```

This will start:
- Django web server (port 8000)
- PostgreSQL database (port 5432)
- Redis (port 6379)
- Kafka (port 9092)
- Celery worker
- Celery beat (scheduler)

3. **Create a superuser (in a new terminal)**
```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Access the application**
- API: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/

### Option 2: Manual Setup (For Development)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/MIraITwowa/crossborder.git
cd crossborder
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Set Up PostgreSQL Database

```bash
# Create database
createdb crossborder

# Or using psql:
psql -U postgres
CREATE DATABASE crossborder;
\q
```

#### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (update with your credentials)
DATABASE_URL=postgresql://postgres:password@localhost:5432/crossborder

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Kafka (optional for now)
KAFKA_BROKER_URL=localhost:9092

# Blockchain (optional for now)
BLOCKCHAIN_PROVIDER_URL=http://localhost:8545
NFT_CONTRACT_ADDRESS=
BLOCKCHAIN_PRIVATE_KEY=

# Dynamic Pricing
DYNAMIC_PRICING_ENABLED=True
PRICE_ADJUSTMENT_THRESHOLD=0.2
PRICING_UPDATE_INTERVAL=300
```

Or update `crossborder_platform/settings.py` directly for development.

#### Step 6: Run Database Migrations

```bash
python manage.py migrate
```

#### Step 7: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

#### Step 8: Start Redis (Required for Celery)

```bash
# On macOS (using Homebrew)
brew services start redis

# On Linux (using systemd)
sudo systemctl start redis

# On Windows (download and run Redis)
redis-server
```

#### Step 9: Start the Development Server

In your main terminal:
```bash
python manage.py runserver
```

#### Step 10: Start Celery Worker (New Terminal)

```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Celery worker
celery -A crossborder_platform worker -l info
```

#### Step 11: Start Celery Beat (New Terminal)

```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Celery beat
celery -A crossborder_platform beat -l info
```

## Verify Installation

1. **Check if the API is running**
```bash
curl http://localhost:8000/api/
```

2. **Access Admin Panel**
- Navigate to http://localhost:8000/admin/
- Login with your superuser credentials

3. **Check Celery**
- You should see periodic tasks running in the Celery worker terminal
- Check logs for "update-product-pricing", "update-interaction-features", etc.

## Load Sample Data (Optional)

Create sample data through the admin panel or Django shell:

```bash
python manage.py shell
```

```python
from users.models import User
from products.models import Category, Product

# Create a test user
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123',
    vip_level='GOLD'
)

# Create a category
category = Category.objects.create(
    name='Watches',
    slug='watches',
    description='Luxury watches'
)

# Create a product
product = Product.objects.create(
    name='Premium Watch',
    slug='premium-watch',
    description='A luxury timepiece',
    category=category,
    product_type='WATCH',
    brand='Rolex',
    base_price=10000.00,
    current_price=10000.00,
    currency='USD',
    stock_quantity=10,
    is_limited_edition=True,
    has_ar_support=True,
    is_active=True
)

print(f"Created: {user}, {category}, {product}")
```

## Troubleshooting

### PostgreSQL Connection Error
- Ensure PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in settings or .env
- Verify database exists: `psql -l`

### Redis Connection Error
- Ensure Redis is running: `redis-cli ping` (should return PONG)
- Check REDIS_HOST and REDIS_PORT in settings

### Celery Not Starting
- Ensure Redis is running
- Check for syntax errors in task files
- Verify CELERY_BROKER_URL is correct

### Import Errors
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

### Migration Errors
- Try: `python manage.py migrate --run-syncdb`
- Or delete db.sqlite3 and run migrations again

## Next Steps

1. **Explore the Admin Panel** - Add products, categories, users
2. **Test the API** - Use tools like Postman or curl
3. **Read API Documentation** - See `API_DOCUMENTATION.md`
4. **Configure Blockchain** - Set up Web3 provider for NFT functionality
5. **Upload 3D Models** - Add AR models for products
6. **Customize** - Modify models, add new features

## Development Tips

- Use `python manage.py shell` for testing models
- Check Celery logs for task execution
- Monitor Redis with `redis-cli monitor`
- Use Django Debug Toolbar for performance optimization
- Enable logging in settings for debugging

## Production Deployment

For production deployment:
1. Set `DEBUG=False`
2. Configure proper `SECRET_KEY`
3. Set up proper database (PostgreSQL)
4. Configure static files serving
5. Set up reverse proxy (nginx)
6. Use gunicorn/uwsgi
7. Enable HTTPS
8. Configure proper CORS settings
9. Set up monitoring and logging
10. Use managed Redis/Kafka services

See Docker setup for containerized deployment approach.

## Support

For issues or questions:
- Check existing issues on GitHub
- Create a new issue with detailed description
- Include error logs and steps to reproduce

Happy coding! 🚀
