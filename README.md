# Wakanda Digital Government Platform

A comprehensive enterprise backend foundation for digital government services built with FastAPI and SQLAlchemy.

## 🏛️ Overview

The Wakanda Digital Government Platform provides a robust, scalable backend infrastructure for modern digital government services. It features advanced modules for user management, job postings, financial analytics, energy monitoring, carbon tracking, AI-powered assistance, and policy management.

## 🚀 Key Features

### Core Modules

- **👥 Users**: Complete user management with role-based authentication
- **💼 Jobs**: Government job postings with advanced search and application management
- **💰 Finance**: Budget management, transaction tracking, and financial analytics
- **⚡ Energy**: Energy consumption monitoring and efficiency tracking
- **🌱 Carbon**: Carbon emissions tracking and offset management
- **🤖 AI**: AI-powered chat and document analysis with OpenRouter integration
- **📋 Policy**: Policy document management with advanced search capabilities

### Advanced Features

- **Authentication & Authorization**: JWT-based security with role management
- **Search & Filtering**: Advanced search capabilities across all modules
- **Analytics & Reporting**: Comprehensive analytics and reporting features
- **AI Integration**: OpenRouter-powered AI assistance and document analysis
- **RESTful API**: Well-documented REST API with automatic OpenAPI documentation
- **Database Integration**: MariaDB support with SQLAlchemy ORM
- **Containerization**: Docker/Podman support for easy deployment

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI 0.104+
- **Database**: MariaDB 10.11+ with SQLAlchemy 2.0+
- **Authentication**: JWT with python-jose
- **AI Integration**: OpenRouter API for chat and analysis
- **Containerization**: Docker/Podman with compose
- **Documentation**: Automatic OpenAPI/Swagger documentation

## 📦 Installation

### Quick Start with Docker/Podman

```bash
git clone https://github.com/Vundla/wakanda-mandate.git
cd wakanda-mandate
cp .env.example .env
# Edit .env with your configuration
podman-compose up -d
```

### Local Development

```bash
git clone https://github.com/Vundla/wakanda-mandate.git
cd wakanda-mandate/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your configuration
python -m uvicorn app.main:app --reload
```

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).

## 🧪 Testing

Run the comprehensive test suite:

```bash
chmod +x test_backend.sh
./test_backend.sh
```

## 📚 API Documentation

Once the application is running:

- **Interactive Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health
- **API Info**: http://localhost:8000/api/v1/info

## 🔧 Configuration

Key environment variables:

- `DATABASE_URL`: MariaDB connection string
- `SECRET_KEY`: JWT signing key (generate a secure 256-bit key)
- `OPENROUTER_API_KEY`: OpenRouter API key for AI features
- `ENVIRONMENT`: Environment (development/production)
- `DEBUG`: Enable debug mode

See `.env.example` for complete configuration options.

## 🏗️ Architecture

```
backend/app/
├── core/          # Core configuration and utilities
├── users/         # User management and authentication
├── jobs/          # Job postings and applications
├── finance/       # Budget and financial management
├── energy/        # Energy monitoring and efficiency
├── carbon/        # Carbon emissions and offsets
├── ai/            # AI integration and chat
├── policy/        # Policy document management
└── main.py        # FastAPI application entry point
```

Each module follows a consistent structure:
- `models.py`: SQLAlchemy database models
- `schemas.py`: Pydantic validation schemas
- `routers.py`: FastAPI route definitions

## 🔐 Security Features

- JWT-based authentication
- Role-based access control (citizen, government_official, admin)
- Password hashing with bcrypt
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration for production deployment

## 🌟 Advanced Capabilities

### AI-Powered Features
- Chat assistance with government-specific context
- Document analysis and summarization
- Policy recommendations
- Data insights and analytics

### Analytics & Reporting
- Financial analytics with budget utilization tracking
- Energy efficiency reporting and recommendations
- Carbon footprint analysis and reduction tracking
- User engagement and system usage statistics

### Search & Discovery
- Full-text search across policy documents
- Advanced job search with multiple filters
- Intelligent recommendations based on user activity
- Citation network analysis for policy documents

## 🚢 Deployment

### Production Considerations

1. **Security**: Change default keys, enable HTTPS, implement rate limiting
2. **Performance**: Configure database connection pooling, caching, reverse proxy
3. **Monitoring**: Set up logging, health checks, performance monitoring
4. **Backup**: Regular database and configuration backups

### Container Deployment

The platform includes production-ready containerization with:
- Multi-stage Docker builds
- Health checks
- Resource limits
- Logging configuration
- Reverse proxy setup with Nginx

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For installation help and troubleshooting:
1. Check the [INSTALLATION.md](INSTALLATION.md) guide
2. Review API documentation at `/api/v1/docs`
3. Run the test script to validate your setup
4. Check application logs for error details

## 🔮 Future Enhancements

- Real-time notifications and messaging
- Mobile API endpoints and SDK
- Advanced AI workflow automation
- Integration with external government systems
- Multi-language support
- Advanced analytics dashboard
- Blockchain integration for document verification

---

Built with ❤️ for digital government transformation.