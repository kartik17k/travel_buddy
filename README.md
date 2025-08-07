# Travel Buddy API 🌍

A professional FastAPI application that generates personalized travel itineraries using AI models (OpenAI, Groq) or static templates. Built with MongoDB for flexible data storage and modern architecture.

## ✨ Features

- **Multiple AI Models**: Support for OpenAI GPT, Groq, and local static responses
- **User Authentication**: Secure registration, login, and JWT-based authentication
- **MongoDB Database**: NoSQL database for flexible data storage and fast queries
- **Itinerary Storage**: Save and retrieve travel plans for authenticated users
- **Structured Responses**: JSON-formatted itineraries with detailed day-by-day plans
- **Flexible Input**: Accepts origin, destination, budget, dates, and model preferences
- **Robust Error Handling**: Graceful fallbacks when AI services are unavailable
- **Professional Architecture**: Clean, maintainable, and scalable codebase
- **Comprehensive Testing**: Full test suite for all endpoints
- **Interactive Documentation**: Auto-generated Swagger/OpenAPI docs

## 🏗️ Project Structure

```
travel_buddy/
├── app/                          # Main application package
│   ├── api/routes/              # API endpoints (health, itinerary, auth)
│   ├── core/                    # Configuration and MongoDB connection
│   ├── models/                  # Request/response schemas & MongoDB models
│   └── services/                # Business logic (AI services, user/itinerary services)
├── tests/                       # Comprehensive test suite
├── main.py                      # FastAPI application entry point
├── init_db.py                   # Database setup script
├── docker-compose.yml           # MongoDB Docker setup
└── requirements.txt             # Dependencies
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd travel_buddy

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup MongoDB

**Option A: Using Docker (Recommended)**
```bash
# Start MongoDB
docker-compose up -d

# MongoDB will be available at: mongodb://localhost:27017
```

**Option B: Local MongoDB Installation**
```bash
# Download and install MongoDB from: https://www.mongodb.com/try/download/community
# Start MongoDB service
mongod

# MongoDB will be available at: mongodb://localhost:27017
```

### 3. Configuration

```bash
# Edit .env file with your settings
# MONGODB_URL=mongodb://localhost:27017
# DATABASE_NAME=travel_buddy
# OPENAI_API_KEY=your_openai_api_key_here (optional)
# GROQ_API_KEY=your_groq_api_key_here (optional)
```

### 4. Initialize Database

```bash
# Initialize MongoDB collections and indexes
python init_db.py
```

### 5. Run the Application

```bash
# Start the server
uvicorn main:app --reload

# Or use the Python environment directly
python -m uvicorn main:app --reload
```

The API will be available at:
- **Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 6. MongoDB Management

Use **MongoDB Compass** to view and manage your database:
- Download: https://www.mongodb.com/products/compass
- Connect to: `mongodb://localhost:27017`
- Database: `travel_buddy`
- Collections: `users`, `itineraries`

## 📡 API Usage

### Authentication

```bash
# Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password123",
    "full_name": "John Doe"
  }'

# Login to get access token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password123"
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Generate Itinerary (Optional Authentication)
```bash
# Without authentication (not saved)
curl -X POST "http://localhost:8000/generate_itinerary" \
  -H "Content-Type: application/json" \
  -d '{
    "from_location": "Mumbai",
    "to_location": "Paris", 
    "budget": 2000,
    "dates": "2025-08-15 to 2025-08-20",
    "model": "local"
  }'

# With authentication (saved to user account)
curl -X POST "http://localhost:8000/generate_itinerary" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "from_location": "Mumbai",
    "to_location": "Paris", 
    "budget": 2000,
    "dates": "2025-08-15 to 2025-08-20",
    "model": "groq"
  }'
```

### View Saved Itineraries
```bash
curl -X GET "http://localhost:8000/my-itineraries" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Request Parameters
- `from_location`: Origin city (e.g., "Mumbai", "New York")
- `to_location`: Destination city (e.g., "Paris", "Tokyo")
- `budget`: Total budget in USD
- `dates`: Travel dates (e.g., "2025-08-15 to 2025-08-20")
- `model`: AI model ("openai", "groq", or "local")

### Response Format
```json
{
  "travel_itinerary": {
    "from_location": "Mumbai",
    "to_location": "Paris",
    "dates": "2025-08-15 to 2025-08-20", 
    "budget": 2000
  },
  "days": [
    {
      "theme": "Travel Day & Arrival",
      "morning": "Departure from Mumbai",
      "afternoon": "Journey to Paris and hotel check-in",
      "evening": "Welcome dinner and local area exploration",
      "budget": 150
    }
  ],
  "summary": {
    "total_estimated_cost": 730,
    "remaining_budget": 1270
  },
  "tips": [
    "Book accommodations in Paris in advance",
    "Try local transportation for authentic experience"
  ]
}
```

## 🛠️ Admin Tools

### User Management CLI
```bash
# List all users
python manage_users.py list

# Create a new user interactively
python manage_users.py create
```

### Database Management
```bash
# Initialize database tables
python init_db.py
```

## 🔐 Authentication

The API includes a complete authentication system with:

- **User Registration & Login**: Secure account creation and authentication
- **JWT Tokens**: Stateless, secure token-based authentication
- **Password Security**: Bcrypt hashing with salt
- **Optional Authentication**: Generate itineraries with or without login
- **Itinerary Storage**: Save travel plans to user accounts
- **Admin Tools**: CLI user management utilities

For detailed authentication documentation, see [AUTH_GUIDE.md](AUTH_GUIDE.md).

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_api/test_health.py -v
python -m pytest tests/test_api/test_itinerary.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

## 🔧 Development

### Adding New Features

1. **New API Endpoints**: Add routes in `app/api/routes/`
2. **Business Logic**: Add services in `app/services/`
3. **Data Models**: Update models in `app/models/`
4. **Configuration**: Modify `app/core/config.py`

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code  
flake8 app/ tests/

# Type checking
mypy app/
```

## 📋 Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- OpenAI SDK (optional)
- Pydantic
- Python-dotenv

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: Check the interactive docs at `/docs`
- **Issues**: Report bugs and feature requests on GitHub
- **Architecture**: See [STRUCTURE.md](STRUCTURE.md) for detailed project structure
