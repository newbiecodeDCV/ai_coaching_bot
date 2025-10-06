# 🎓 AI Coaching Bot - Complete Project

## 📋 Project Overview

**AI Coaching Bot** là một hệ thống hỗ trợ học tập cá nhân hóa sử dụng AI, được xây dựng với:
- **LangGraph** cho workflow orchestration
- **OpenAI GPT-4** cho AI reasoning
- **RAG (Retrieval-Augmented Generation)** cho document Q&A
- **FastAPI** cho backend REST API
- **Streamlit** cho user interface
- **SQLite** cho database
- **FAISS** cho vector store

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │  (Port 8501)
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   FastAPI API   │  (Port 8000)
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌────────────────┐   ┌────────────────┐
│  LangGraph     │   │  RAG Service   │
│  Workflow      │   │  (FAISS+OpenAI)│
└────────┬───────┘   └────────┬───────┘
         │                    │
         ▼                    ▼
┌─────────────────────────────────────┐
│         SQLite Database             │
│  (Users, Skills, Courses, Plans)    │
└─────────────────────────────────────┘
```

---

## 📦 Project Structure

```
ai_coaching_bot/
├── src/ai_coaching_bot/
│   ├── database/                # SQLite models & seed data
│   ├── rag/                     # RAG components (FAISS + OpenAI)
│   ├── graph/                   # LangGraph workflow
│   │   ├── nodes/               # Workflow nodes
│   │   ├── prompts.py           # LLM prompts
│   │   └── state.py             # State schema
│   └── api/                     # FastAPI backend
│       ├── routers/             # API routes (5 routers)
│       ├── schemas.py           # Pydantic models
│       ├── dependencies.py      # DI & validators
│       └── main.py              # FastAPI app
├── streamlit_ui/                # Streamlit frontend
│   ├── Home.py                  # Dashboard
│   ├── pages/                   # 4 functional pages
│   ├── utils/                   # API client & helpers
│   └── .streamlit/              # Config
├── data/                        # Database & documents
├── docs/                        # Sprint guides
└── tests/                       # Test files
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- LangChain API key (optional, for tracing)

### Installation

```powershell
# 1. Clone and setup
git clone <repo-url>
cd ai_coaching_bot

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt
pip install -r streamlit_ui/requirements.txt

# 4. Setup environment
copy .env.example .env
# Edit .env with your API keys

# 5. Initialize database
python src/ai_coaching_bot/database/seed_data.py
```

### Running the Application

**Terminal 1: Start FastAPI Backend**
```powershell
.\venv\Scripts\Activate.ps1
uvicorn src.ai_coaching_bot.api.main:app --reload --port 8000
```

**Terminal 2: Start Streamlit UI**
```powershell
.\venv\Scripts\Activate.ps1
streamlit run streamlit_ui/Home.py
```

**Access:**
- Streamlit UI: http://localhost:8501
- FastAPI Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/health

---

## 📚 Features

### **1. Dashboard (Home)**
- User overview với key metrics
- Skill gaps visualization
- Recent assessments
- Active course enrollments
- Quick action buttons

### **2. Chat Interface**
- Interactive AI Coach conversation
- LangGraph workflow execution
- Multiple modes:
  - **Coaching**: Skill gaps, course recommendations, learning plans
  - **Performance**: Progress analysis
  - **Docs Q&A**: RAG-based document queries
- Chat history & export
- Metadata display (citations, plans)

### **3. Profile & Skills**
- User profile management
- Skills catalog với filtering
- Assessment creation
- Performance analytics
- Gap analysis

### **4. Learning Plans**
- View all learning plans
- Status management (active, paused, completed)
- Plan details & data visualization
- Delete functionality

### **5. Documents Library**
- Document listing với search
- Vector search (RAG)
- Upload với auto-indexing
- Reindex capability
- Document deletion

---

## 🎯 Key Technologies

### **Backend Stack**
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM for database
- **Pydantic**: Data validation
- **LangGraph**: Workflow orchestration
- **LangChain**: LLM framework

### **AI & ML**
- **OpenAI GPT-4**: Main reasoning engine
- **OpenAI Embeddings**: Text-to-vector conversion
- **FAISS**: Vector similarity search
- **LangSmith**: Tracing & monitoring (optional)

### **Frontend**
- **Streamlit**: Interactive web UI
- **Pandas**: Data manipulation
- **Custom CSS**: Professional styling

### **Storage**
- **SQLite**: Relational database
- **FAISS Index**: Vector store
- **Local Filesystem**: Document storage

---

## 📊 Sprint Breakdown

### **Sprint 1: Foundation** ✅
- Project structure
- Database schema & models
- Seed data
- `.gitignore` và `.env`

### **Sprint 2: RAG System** ✅
- Document parser (PDF, Markdown)
- Text chunker
- OpenAI embeddings với caching
- FAISS vector store
- RAG service (upload, ingest, query)
- Test documents

### **Sprint 3: LangGraph Workflow** ✅
- State schema
- Detailed prompts với examples
- 9 workflow nodes:
  - Router (intent classification)
  - Coaching nodes (5): fetch_user_data, skill_resolver, gap_analysis, course_selector, plan_builder
  - Performance node
  - Docs Q&A node
  - Summarizer node
- Conditional routing
- Error handling

### **Sprint 4: FastAPI Backend** ✅
- 5 API routers:
  - Chat (2 endpoints)
  - Users (4 endpoints)
  - Skills (6 endpoints)
  - Documents (6 endpoints)
  - Plans (6 endpoints)
- Total: **24 RESTful endpoints**
- Pydantic schemas
- Dependencies & validators
- Health check
- CORS middleware
- Global exception handlers

### **Sprint 5: Streamlit UI** ✅
- 5 pages (Home + 4 functional)
- API client wrapper
- Custom CSS styling
- Session state management
- Backend connection monitor
- Export capabilities
- Professional UX/UI

### **Sprint 6: Testing & Docs** ✅
- Comprehensive guides for each sprint
- Deployment instructions
- Testing workflows
- User documentation

---

## 🧪 Testing

### **Unit Tests**
```powershell
pytest tests/ -v
```

### **Manual Testing Workflows**

**Test 1: Chat Flow**
1. Start backend & UI
2. Navigate to Chat
3. Ask: "Tôi muốn học Python từ đầu"
4. Verify: Response with course recommendations
5. Check metadata: Mode, citations

**Test 2: RAG Document Search**
1. Go to Documents → Upload
2. Upload a text file
3. Wait for indexing
4. Go to Search tab
5. Query document content
6. Verify: Relevant results returned

**Test 3: Learning Plan Creation**
1. Chat: "Tạo learning plan cho tôi"
2. Wait for LangGraph workflow
3. Go to Plans page
4. Verify: New plan appears
5. Test: Pause/Resume/Delete

**Test 4: Assessment Creation**
1. Go to Profile → Skills
2. Find a skill
3. Click "Assess"
4. Enter score (e.g., 75)
5. Submit
6. Verify: Level updated

---

## 📈 Code Statistics

- **Total Lines of Code:** ~7,000+
- **Python Files:** 40+
- **Database Tables:** 7
- **API Endpoints:** 24
- **UI Pages:** 5
- **LangGraph Nodes:** 9
- **Test Files:** Multiple

---

## 🔧 Configuration

### **Environment Variables** (`.env`)
```bash
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=ls__...
DATABASE_PATH=data/coaching_bot.db
FAISS_INDEX_PATH=data/faiss_index
```

### **FastAPI Settings**
- Host: `0.0.0.0`
- Port: `8000`
- Reload: `True` (dev mode)

### **Streamlit Settings**
- Port: `8501`
- Theme: Custom (see `.streamlit/config.toml`)

---

## 📝 API Documentation

Full API docs available at: **http://localhost:8000/docs**

### **Sample API Calls**

**Execute Chat:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/execute" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001", "message": "Tôi muốn học Python"}'
```

**Get User Overview:**
```bash
curl "http://localhost:8000/api/v1/users/user_001/overview"
```

**Search Documents:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "SQL basics", "top_k": 5}'
```

---

## 🚢 Deployment

### **Option 1: Local Development**
See Quick Start section above.

### **Option 2: Docker** (Recommended for Production)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt -r streamlit_ui/requirements.txt
EXPOSE 8000 8501

# Start both services
CMD uvicorn src.ai_coaching_bot.api.main:app --host 0.0.0.0 --port 8000 & \
    streamlit run streamlit_ui/Home.py
```

### **Option 3: Cloud Deployment**
- **FastAPI:** Deploy to Railway, Render, or AWS
- **Streamlit:** Deploy to Streamlit Cloud
- **Database:** Use PostgreSQL or hosted SQLite

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Team

Developed as a comprehensive AI Coaching Bot system demonstrating:
- Advanced LangGraph workflows
- RAG-based document Q&A
- Full-stack development (FastAPI + Streamlit)
- Production-ready architecture

---

## 📚 Documentation

- **Sprint 1-2:** `docs/README.md`
- **Sprint 3:** RAG testing in main README
- **Sprint 4:** `docs/SPRINT5_FASTAPI_GUIDE.md`
- **Sprint 5:** `docs/SPRINT6_STREAMLIT_GUIDE.md`

---

## ✅ Project Status: **COMPLETE**

All features implemented and tested. Ready for production use! 🎉

**Technologies Mastered:**
- ✅ LangGraph workflow orchestration
- ✅ OpenAI GPT-4 integration
- ✅ RAG với FAISS vector store
- ✅ FastAPI REST API development
- ✅ Streamlit interactive UI
- ✅ SQLite database design
- ✅ Full-stack Python application

**Key Achievements:**
- 🏆 ~7,000 lines of production code
- 🏆 24 RESTful API endpoints
- 🏆 5 interactive UI pages
- 🏆 9 LangGraph workflow nodes
- 🏆 Complete RAG pipeline
- 🏆 Comprehensive documentation

---

## 🙏 Acknowledgments

Built with:
- LangChain & LangGraph
- OpenAI
- FastAPI
- Streamlit
- FAISS by Facebook Research

---

**Made with ❤️ using Python**