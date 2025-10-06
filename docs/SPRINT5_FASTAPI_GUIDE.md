# Sprint 5: FastAPI Backend - Completion Guide

## ✅ Completed Components

### 1. **API Routers** (5 routers with full CRUD operations)

#### 📁 `api/routers/chat.py`
- **POST** `/chat/execute` - Execute full LangGraph workflow (coaching/performance)
- **POST** `/chat/route` - Classify intent only (without full execution)

#### 📁 `api/routers/users.py`
- **GET** `/users/{user_id}` - Get user profile
- **GET** `/users/{user_id}/overview` - Get user overview (assessments, enrollments, gaps, stats)
- **GET** `/users/{user_id}/assessments` - Get user assessments (with filtering)
- **GET** `/users/{user_id}/enrollments` - Get user enrollments (with status filter)

#### 📁 `api/routers/skills.py`
- **GET** `/skills/` - List all skills (with pagination, search, category filter)
- **GET** `/skills/{skill_id}` - Get skill details
- **GET** `/skills/{skill_id}/stats` - Get skill with statistics
- **POST** `/skills/{skill_id}/assess` - Create new assessment for user
- **GET** `/skills/categories/` - Get categories with counts
- **GET** `/skills/user/{user_id}/` - Get user's skills with assessment levels

#### 📁 `api/routers/documents.py`
- **GET** `/documents/` - List documents (with filters and pagination)
- **GET** `/documents/{document_id}` - Get document details
- **POST** `/documents/upload` - Upload new document (auto-indexes into RAG)
- **POST** `/documents/search` - Search documents using vector search
- **DELETE** `/documents/{document_id}` - Delete document and cleanup files
- **PUT** `/documents/{document_id}/reindex` - Reindex document
- **GET** `/documents/types/` - Get document types with counts

#### 📁 `api/routers/plans.py`
- **GET** `/plans/user/{user_id}` - Get user's learning plans
- **GET** `/plans/{plan_id}` - Get plan details
- **POST** `/plans/user/{user_id}` - Create new learning plan
- **PUT** `/plans/{plan_id}/status` - Update plan status
- **DELETE** `/plans/{plan_id}` - Delete learning plan
- **GET** `/plans/` - List all plans (admin)

### 2. **Core Components**

#### 📁 `api/schemas.py`
- Complete Pydantic schemas for all requests/responses
- Input validation with Field constraints
- Vietnamese docstrings

#### 📁 `api/dependencies.py`
- Database session management (`get_db`)
- Input validators (`validate_user_id`, `validate_message`)
- Reusable dependency injection

#### 📁 `api/main.py`
- FastAPI application with all routers
- CORS middleware
- Health check endpoint
- Global exception handlers
- Database initialization on startup
- Comprehensive error handling

---

## 🚀 How to Run the FastAPI Server

### Step 1: Ensure Environment is Ready
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Check .env file exists with required variables
cat .env
# Should contain:
# OPENAI_API_KEY=your_key_here
# LANGCHAIN_API_KEY=your_key_here
# DATABASE_PATH=data/coaching_bot.db
```

### Step 2: Install FastAPI Dependencies (if not already)
```powershell
pip install fastapi uvicorn python-multipart
```

### Step 3: Run the Server
```powershell
# Option 1: Using uvicorn directly
uvicorn src.ai_coaching_bot.api.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python module
python -m uvicorn src.ai_coaching_bot.api.main:app --reload --port 8000

# Option 3: Run as script
python -m src.ai_coaching_bot.api.main
```

### Step 4: Access the API
- **API Root**: http://localhost:8000/
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🧪 Testing the API

### Using Swagger UI (Recommended for Quick Testing)
1. Navigate to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in parameters and request body
4. Click "Execute"
5. View response

### Using cURL

#### Test Chat Workflow
```powershell
curl -X POST "http://localhost:8000/api/v1/chat/execute" `
  -H "Content-Type: application/json" `
  -d '{\"user_id\": \"user_001\", \"message\": \"Tôi muốn học Python\"}'
```

#### Test User Profile
```powershell
curl "http://localhost:8000/api/v1/users/user_001"
```

#### Test User Overview
```powershell
curl "http://localhost:8000/api/v1/users/user_001/overview"
```

#### Test Skills List
```powershell
curl "http://localhost:8000/api/v1/skills/?category=programming"
```

#### Test Document Search
```powershell
curl -X POST "http://localhost:8000/api/v1/documents/search" `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"SQL basics\", \"top_k\": 5}'
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Test chat
response = requests.post(
    f"{BASE_URL}/chat/execute",
    json={"user_id": "user_001", "message": "Tôi muốn cải thiện kỹ năng SQL"}
)
print(response.json())

# Test user overview
response = requests.get(f"{BASE_URL}/users/user_001/overview")
print(response.json())

# Test skills
response = requests.get(f"{BASE_URL}/skills/")
print(response.json())

# Test document upload
files = {'file': open('path/to/document.pdf', 'rb')}
data = {
    'title': 'SQL Tutorial',
    'description': 'Beginner SQL guide',
    'doc_type': 'tutorial',
    'tags': 'sql,database,beginner'
}
response = requests.post(f"{BASE_URL}/documents/upload", files=files, data=data)
print(response.json())
```

---

## 📊 API Endpoints Overview

### **Chat Endpoints** (2 endpoints)
- Execute workflow with full AI processing
- Route classification for intent detection

### **User Endpoints** (4 endpoints)
- Profile management
- Comprehensive overview with stats
- Assessment history
- Enrollment tracking

### **Skills Endpoints** (6 endpoints)
- Skill catalog with search
- Detailed skill information
- Assessment creation
- User skill mapping
- Category management

### **Documents Endpoints** (6 endpoints)
- Document library management
- Upload with auto-indexing
- Vector-based search
- Reindexing capability
- Type categorization

### **Plans Endpoints** (6 endpoints)
- Learning plan CRUD
- Status management
- User-specific plans
- Admin overview

**Total: 24 RESTful endpoints** serving the AI Coaching Bot!

---

## 🔧 Architecture Highlights

### Dependency Injection
- Clean separation of concerns
- Reusable database sessions
- Input validation at dependency level

### Error Handling
- Comprehensive try-except blocks
- HTTP status codes (400, 404, 500)
- Detailed error messages
- Global exception handlers

### Integration
- **LangGraph**: Chat router invokes full workflow
- **RAG Service**: Documents router auto-indexes uploads
- **Database**: All routers use SQLAlchemy ORM
- **Pydantic**: Strong typing and validation

### Best Practices
- Async/await for I/O operations
- Query parameter validation
- Pagination support
- Filter capabilities
- Response models ensure consistency

---

## 📝 Next Steps (Future Enhancements)

1. **Authentication & Authorization**
   - JWT tokens
   - Role-based access control
   - User registration/login

2. **Rate Limiting**
   - Prevent abuse
   - Throttle requests

3. **Caching**
   - Redis for frequent queries
   - Cache user profiles
   - Cache skill catalog

4. **Background Tasks**
   - Async document processing
   - Email notifications
   - Scheduled reports

5. **Monitoring**
   - Prometheus metrics
   - Application logs
   - Performance tracking

6. **Testing**
   - Unit tests for routers
   - Integration tests
   - API endpoint tests with pytest

---

## ✅ Sprint 5 Status: **COMPLETE**

All FastAPI backend endpoints are implemented with:
- ✅ Clean architecture
- ✅ Comprehensive error handling
- ✅ Vietnamese documentation
- ✅ Pydantic validation
- ✅ Database integration
- ✅ LangGraph workflow integration
- ✅ RAG service integration
- ✅ Health checks
- ✅ CORS support
- ✅ Auto-generated API docs

**Ready for Sprint 6: Streamlit UI Development!** 🎉