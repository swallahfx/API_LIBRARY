
<<<<<<< HEAD
# ============================================================================
# README.md - Project Documentation
# ============================================================================

# Create: README.md
=======
>>>>>>> staging
# 🧠 AI Knowledge Library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A production-ready intelligent document search and Q&A system built with **FastAPI**, **MongoDB**, **LangChain**, and **OpenAI**. Perfect demonstration project for backend developer interviews.

## ✨ Features

### 🤖 **AI-Powered Capabilities**
- **Intelligent Q&A**: Ask questions about your documents in natural language
- **Semantic Search**: Vector-based similarity search using FAISS
- **Document Understanding**: Automatic text extraction and chunking
- **Source Attribution**: Get answers with source citations

### 📄 **Document Management**
- **Multi-format Support**: PDF, TXT, CSV, DOCX files
- **Metadata Management**: Title, author, category, tags
- **Batch Processing**: Background document processing
- **Version Control**: Track document changes and updates

### 🏗️ **Production-Ready Architecture**
- **Async/Await**: Non-blocking operations throughout
- **Microservices**: Clean separation of concerns
- **Caching**: Redis for query result caching
- **Monitoring**: Health checks and analytics
- **Docker**: Complete containerization

### 🎨 **Modern Frontend**
- **Beautiful UI**: Gradient design with smooth animations
- **Responsive**: Works on desktop and mobile
- **Interactive**: Drag & drop file uploads
- **Real-time**: Live analytics and notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key

### 1. Clone and Setup
```bash
git clone https://github.com/your-username/ai-knowledge-library.git
cd ai-knowledge-library
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
```

### 3. Deploy with Docker
```bash
./deploy.sh
```

### 4. Access Application
- **Frontend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health/

## 📋 Manual Installation

```bash
# Install dependencies
make install

# Start databases
docker run -d -p 27017:27017 --name mongo mongo:7.0
docker run -d -p 6379:6379 --name redis redis:7.2-alpine

# Initialize database
make init-db

# Load sample data
make load-sample-data

# Run development server
make dev
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   AI Services   │
│   (HTML/JS)     │◄──►│   Application   │◄──►│   (LangChain)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Redis       │◄──►│    MongoDB      │    │   OpenAI API    │
│   (Caching)     │    │  (Documents)    │    │   (GPT/Embed)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ FAISS Vector    │
                       │     Store       │
                       └─────────────────┘
```

## 🔧 API Endpoints

### Documents
- `POST /api/v1/documents/upload` - Upload documents
- `GET /api/v1/documents/` - List documents
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete document

### Queries
- `POST /api/v1/queries/ask` - Ask questions
- `GET /api/v1/queries/history` - Query history
- `GET /api/v1/queries/{id}` - Get query details

### Analytics
- `GET /api/v1/analytics/` - System analytics
- `GET /api/v1/analytics/documents` - Document analytics
- `GET /api/v1/analytics/queries` - Query analytics

### Health
- `GET /health/` - Comprehensive health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test types
make test-unit          # Unit tests
make test-integration   # Integration tests

# Run with coverage
pytest --cov=app --cov-report=html
```

## 🔍 Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
mypy app/

# Security check
make security-check
```

## 📊 Performance Features

### **Async Operations**
- Non-blocking file processing
- Concurrent database operations
- Async HTTP requests

### **Caching Strategy**
- Redis query result caching
- Vector store persistence
- Database connection pooling

### **Optimization**
- Background task processing
- Efficient text chunking
- Optimized database indexes

## 🔒 Security Features

### **Input Validation**
- Pydantic model validation
- File type restrictions
- Size limit enforcement

### **Error Handling**
- Graceful error recovery
- Detailed error logging
- User-friendly error messages

### **Production Security**
- Environment variable configuration
- Secure headers
- Rate limiting ready

## 📈 Monitoring & Analytics

### **Health Monitoring**
- Service status checks
- Database connectivity
- Vector store readiness

### **Usage Analytics**
- Query performance metrics
- Document processing stats
- User activity tracking

### **Logging**
- Structured application logs
- Error tracking
- Performance monitoring

## 🎯 Interview Preparation

This project demonstrates expertise in:

### **Required Technologies**
- ✅ **FastAPI**: Advanced async API development
- ✅ **MongoDB**: Document storage with Motor driver
- ✅ **LangChain**: AI pipeline implementation
- ✅ **Models**: Pydantic for data validation

### **Technical Skills**
- ✅ **Async Programming**: Throughout the application
- ✅ **Database Design**: Optimized schemas and indexes
- ✅ **API Design**: RESTful endpoints with documentation
- ✅ **Error Handling**: Comprehensive error management
- ✅ **Testing**: Unit and integration test suites
- ✅ **Docker**: Production-ready containerization

### **Problem Solving**
- ✅ **Complex Data Processing**: Document parsing and chunking
- ✅ **AI Integration**: Vector embeddings and similarity search
- ✅ **Performance Optimization**: Caching and async operations
- ✅ **Production Deployment**: Complete CI/CD pipeline

## 🚀 Deployment Options

### **Development**
```bash
make dev                # Local development
make dev-docker         # Docker development
```

### **Production**
```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Kubernetes (manifests in deployment/kubernetes/)
kubectl apply -f deployment/kubernetes/
```

## 📚 Project Structure

```
ai_library/
├── app/                    # Main application
│   ├── api/               # API endpoints
│   ├── core/              # Core configurations
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── frontend/              # Web interface
├── tests/                 # Test suites
├── scripts/               # Utility scripts
├── docker/                # Docker configurations
├── deployment/            # Deployment configs
└── docs/                  # Documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent framework
- **LangChain** for AI pipeline tools
- **OpenAI** for language models
- **MongoDB** for flexible document storage

---

**Built with ❤️ for the Aricah Backend Developer Interview**

*Demonstrating production-ready FastAPI development with AI integration*