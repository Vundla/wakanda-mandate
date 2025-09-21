# Wakanda Digital Government Platform - Installation Guide

This guide provides step-by-step instructions for setting up and running the Wakanda Digital Government Platform backend.

## Prerequisites

- Python 3.11 or higher
- MariaDB 10.11 or higher
- Podman or Docker (for containerized deployment)
- Git

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Vundla/wakanda-mandate.git
cd wakanda-mandate
```

### 2. Backend Setup

#### Create Python Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Environment Configuration

```bash
# Copy environment template
cp ../.env.example .env

# Edit .env file with your configuration
nano .env
```

**Important Environment Variables:**
- `DATABASE_URL`: MariaDB connection string
- `SECRET_KEY`: JWT secret key (generate a secure 256-bit key)
- `OPENROUTER_API_KEY`: Your OpenRouter API key for AI features

### 3. Database Setup

#### Install and Start MariaDB

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mariadb-server mariadb-client

# CentOS/RHEL
sudo yum install mariadb-server mariadb

# Start MariaDB service
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

#### Configure Database

```bash
# Secure installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE wakanda_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'vundla'@'localhost' IDENTIFIED BY 'Mv@20217$';
GRANT ALL PRIVILEGES ON wakanda_db.* TO 'vundla'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Run the Application

```bash
# From the backend directory
cd app
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Docs**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health
- **API Info**: http://localhost:8000/api/v1/info

## Containerized Deployment with Podman Compose

### 1. Install Podman

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install podman podman-compose

# CentOS/RHEL
sudo dnf install podman podman-compose

# Or use Docker if preferred
sudo apt install docker.io docker-compose
```

### 2. Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Set your OpenRouter API key
export OPENROUTER_API_KEY=your_api_key_here
```

### 3. Deploy with Podman Compose

```bash
# Build and start all services
podman-compose up -d

# Or with Docker
docker-compose up -d
```

### 4. Check Service Status

```bash
# Check running containers
podman-compose ps

# View logs
podman-compose logs backend
podman-compose logs database

# Health check
curl http://localhost:8000/health
```

## Testing the Installation

### 1. Backend Health Check Script

Create and run the test script:

```bash
#!/bin/bash
# File: test_backend.sh

echo "Testing Wakanda Digital Government Platform Backend..."

# Health check
echo "1. Health Check:"
curl -s http://localhost:8000/health | jq '.'

# API Info
echo -e "\n2. API Info:"
curl -s http://localhost:8000/api/v1/info | jq '.'

# Register test user
echo -e "\n3. User Registration:"
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@wakanda.gov",
    "username": "testuser",
    "full_name": "Test User",
    "password": "testpassword123",
    "role": "citizen"
  }' | jq '.'

# Login test user
echo -e "\n4. User Login:"
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Login successful, token received"

# Test authenticated endpoint
echo -e "\n5. Authenticated Request (User Profile):"
curl -s -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# Test job search
echo -e "\n6. Job Search:"
curl -s "http://localhost:8000/api/v1/jobs/search?keyword=developer" | jq '.'

# Test policy search
echo -e "\n7. Policy Search:"
curl -s "http://localhost:8000/api/v1/policy/documents/search?query=government" | jq '.'

echo -e "\n✅ Backend testing completed!"
```

```bash
chmod +x test_backend.sh
./test_backend.sh
```

### 2. Advanced Feature Testing

Test each module's advanced features:

```bash
# AI Chat (requires OpenRouter API key)
curl -X POST "http://localhost:8000/api/v1/ai/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What government services are available?",
    "model": "openai/gpt-3.5-turbo"
  }'

# Energy statistics
curl -X GET "http://localhost:8000/api/v1/energy/stats" \
  -H "Authorization: Bearer $TOKEN"

# Carbon emissions summary
curl -X GET "http://localhost:8000/api/v1/carbon/summary" \
  -H "Authorization: Bearer $TOKEN"

# Finance analytics
curl -X GET "http://localhost:8000/api/v1/finance/analytics" \
  -H "Authorization: Bearer $TOKEN"
```

## Configuration Reference

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | MariaDB connection string | None | Yes |
| `SECRET_KEY` | JWT signing key | None | Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key | None | No |
| `ENVIRONMENT` | Environment name | development | No |
| `DEBUG` | Enable debug mode | true | No |

### Database Schema

The application automatically creates all necessary tables on startup. The schema includes:

- **Users**: User accounts and authentication
- **Jobs**: Job postings and applications
- **Budgets/Transactions**: Financial management
- **Energy Sources/Consumption**: Energy tracking
- **Emission Sources/Carbon Emissions**: Carbon monitoring
- **Policy Documents**: Policy management
- **AI Chat Sessions/Messages**: AI interactions

## Production Deployment Considerations

### 1. Security

- Change the default `SECRET_KEY` to a secure 256-bit key
- Use environment variables for all sensitive configuration
- Enable HTTPS with proper SSL certificates
- Implement rate limiting and API key authentication
- Regular security updates

### 2. Performance

- Configure database connection pooling
- Implement Redis caching
- Use a reverse proxy (Nginx/Apache)
- Enable compression and static file serving
- Monitor application performance

### 3. Monitoring

- Set up logging and log aggregation
- Configure health checks and alerts
- Monitor database performance
- Track API usage and errors

### 4. Backup

- Regular database backups
- Application configuration backups
- File upload storage backups

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MariaDB service status
   - Verify database credentials
   - Ensure database exists

2. **Port Already in Use**
   - Check for running processes: `lsof -i :8000`
   - Change port in configuration

3. **Permission Denied**
   - Check file permissions
   - Ensure proper user ownership

4. **Module Import Errors**
   - Verify virtual environment activation
   - Check Python version compatibility
   - Reinstall dependencies

### Getting Help

- Check the API documentation at `/api/v1/docs`
- Review application logs
- Verify environment configuration
- Test database connectivity

## Next Steps

After successful installation:

1. Create admin user accounts
2. Configure government departments
3. Import initial policy documents
4. Set up energy and carbon monitoring
5. Configure AI chat system
6. Customize for specific government needs

For additional support and advanced configuration, please refer to the API documentation and module-specific guides.