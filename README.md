# AI Coaching Bot

Hệ thống AI Agent hỗ trợ đào tạo và phát triển kỹ năng cá nhân hóa.

## 🎯 Chức năng chính

### 1. AI Coaching
- **General**: Tạo lộ trình học theo role/level/mục tiêu
- **Skill-specific**: Tạo kế hoạch học cho kỹ năng cụ thể khi user yêu cầu

### 2. Phân tích hiệu suất
- Tự động lấy dữ liệu điểm số, khóa học theo `user_id`
- Phân tích gap và đưa ra gợi ý cải thiện

### 3. Tra cứu + Hỏi–đáp tài liệu (RAG)
- Tra cứu tài liệu nội bộ
- Hỏi–đáp trên tài liệu với trích dẫn nguồn

## 🏗️ Kiến trúc

```
┌─────────────┐
│  Streamlit  │ (Chat + Dashboard + Docs)
│     UI      │
└──────┬──────┘
       │
┌──────▼──────┐
│   FastAPI   │ (Không cho user chỉnh model)
│   Backend   │
└──────┬──────┘
       │
┌──────▼──────┐
│  LangGraph  │ (Intent Router → Subgraphs)
│ Orchestrator│
└──────┬──────┘
       │
   ┌───┴───┐
   ▼       ▼
┌──────┐ ┌────────┐
│SQLite│ │ FAISS  │
│  DB  │ │ Vector │
└──────┘ └────────┘
```

## 📁 Cấu trúc thư mục

```
ai_coaching_bot/
├── src/ai_coaching_bot/
│   ├── __init__.py
│   ├── config.py              # Config loader
│   ├── database/              
│   │   ├── base.py            # SQLAlchemy base
│   │   ├── models.py          # ORM models
│   │   └── seed.py            # Seed data
│   ├── services/              # Business logic (TODO)
│   ├── rag/                   # RAG components (TODO)
│   ├── graph/                 # LangGraph nodes (TODO)
│   └── api/                   # FastAPI endpoints (TODO)
├── data/                      # SQLite database
├── docs/demo_docs/            # Demo documents
├── faiss_index/               # FAISS vector store
├── tests/                     # Tests (TODO)
├── setup_db.py                # Database setup script
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Cài đặt dependencies

```bash
# Tạo virtual environment
python -m venv venv

# Activate (Windows)
.\\venv\\Scripts\\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Cấu hình environment

```bash
# Copy template
copy .env.example .env

# Sửa .env với API keys thực của bạn
# OPENAI_API_KEY=sk-...
# LANGSMITH_API_KEY=... (optional)
```

### 3. Setup database

```bash
python setup_db.py
```

Output mong đợi:
```
📦 Setup database tại: sqlite:///./data/coaching_bot.db
🔨 Đang tạo tables...
✅ Tables đã được tạo
🌱 Bắt đầu seed dữ liệu...
✅ Skills seeded
✅ Courses seeded
✅ Users seeded
✅ Assessments seeded
✅ Enrollments seeded
✅ Documents seeded
🎉 Seed hoàn tất!
```

## 📊 Database Schema

### Users
- id, name, email, role, level (1-5), time_budget_per_week

### Skills
- id, name, synonyms (JSON), weight, description
- Prerequisites: many-to-many

### Courses
- id, title, provider, url, duration_hours, cost
- CourseSkill: link với skills + min_level

### Assessments
- user_id, skill_id, score, level, taken_at

### Enrollments
- user_id, course_id, status, progress_percent

### Learning Plans
- user_id, title, status
- PlanItem: week_no, target, course_id, kpi

### Documents & Chunks
- Document: title, source_path, skill_id
- DocChunk: text, page (vector trong FAISS)

## 🔧 Triển khai tiếp theo

### Sprint 3: RAG Components (TODO)
- [ ] PDF parser (pdfplumber)
- [ ] Text chunking (800-1200 tokens)
- [ ] Embedding service (OpenAI)
- [ ] FAISS index manager
- [ ] Document upload/ingest service

### Sprint 4: LangGraph (TODO)
- [ ] State schema (Pydantic)
- [ ] Intent router
- [ ] Coaching nodes (general + skill)
- [ ] Performance analysis node
- [ ] Docs-QA node with RAG
- [ ] Summarizer

### Sprint 5: FastAPI Backend (TODO)
- [ ] `/chat/execute` - Main chat endpoint
- [ ] `/users/{id}` - User profile
- [ ] `/users/{id}/overview` - Performance overview
- [ ] `/skills/search` - Skill resolver
- [ ] `/documents/upload` - Upload docs
- [ ] `/documents/query` - RAG query
- [ ] `/plans/{user_id}/confirm` - Save plan

### Sprint 6: Streamlit UI (TODO)
- [ ] Chat page với mode selector
- [ ] Dashboard (scores, progress, enrollments)
- [ ] Documents page (upload + query)
- [ ] Session management

### Sprint 7: Testing (TODO)
- [ ] Unit tests cho services
- [ ] Integration tests cho LangGraph flows
- [ ] LangSmith tracing setup

### Sprint 8: Documentation (TODO)
- [ ] Architecture diagram
- [ ] API documentation
- [ ] Deployment guide

## 🔐 Bảo mật

- ❌ Không commit `.env` file
- ✅ Sử dụng `.env.example` làm template
- ✅ GitHub push protection đã setup qua `.gitignore`
- ✅ User không có quyền chỉnh model (cố định ở server)

## 📝 Dữ liệu mô phỏng

### Users demo
- `user_001`: Nguyễn Văn A (Data Analyst, level 2)
- `user_002`: Trần Thị B (Junior Developer, level 1)
- `user_003`: Lê Văn C (Business Analyst, level 3)

### Skills
10 skills: SQL, Python, Data Analysis, Visualization, ML Basics, Communication, Leadership, Excel, Statistics, Git

### Courses
10 courses map với skills + min_level

## 🤝 Contributing

Cấu trúc code:
- Docstring tiếng Việt đầy đủ
- Type hints cho functions
- Tuân thủ PEP 8
- Test coverage > 70%

## 📄 License

Internal use only.

## 🐛 Known Issues

- [ ] Cần implement RAG components
- [ ] Cần implement LangGraph workflow
- [ ] Cần implement FastAPI endpoints
- [ ] Cần implement Streamlit UI

## 📞 Support

Liên hệ: [Your Email]
