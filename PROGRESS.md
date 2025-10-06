# TIẾN ĐỘ TRIỂN KHAI

## ✅ Đã hoàn thành (Sprints 0-3)

### Sprint 0: Setup môi trường ✅
- `.gitignore` với rules đầy đủ
- `.env.example` template (không chứa secret)
- `requirements.txt` với tất cả dependencies
- Cấu trúc thư mục chuẩn

### Sprint 1: Database ✅
- **10 SQLAlchemy models**: User, Skill, SkillPrerequisite, Course, CourseSkill, Assessment, Enrollment, LearningPlan, PlanItem, Document, DocChunk
- **Seed script** với dữ liệu mô phỏng:
  - 10 skills (SQL, Python, Data Analysis, etc.)
  - 10 courses với mapping skills
  - 3 users demo
  - Assessments và enrollments mẫu
- `setup_db.py` script để init DB

### Sprint 2: Config ✅
- `config.py` với Pydantic Settings
- Environment loader từ `.env`
- Auto-create directories (data/, faiss_index/, logs/)

### Sprint 3: RAG Components ✅
- **Parser** (`parser.py`): PDF, Markdown, TXT support
- **Chunker** (`chunker.py`): Smart chunking với overlap, giữ page metadata
- **Embedder** (`embedder.py`): OpenAI embeddings với file-based cache
- **VectorStore** (`vector_store.py`): FAISS index manager
- **RAGService** (`service.py`): Orchestration - upload/ingest/query
- **Demo docs**: 2 markdown files (training policy, SQL guide)

---

## 🚧 Đang làm (Sprint 4)

### Sprint 4: LangGraph Workflow

**Files cần tạo:**
```
src/ai_coaching_bot/graph/
├── __init__.py
├── state.py           # Pydantic State schema
├── prompts.py         # System prompts
├── nodes/
│   ├── __init__.py
│   ├── router.py      # Intent router
│   ├── coaching.py    # Coaching nodes (general + skill)
│   ├── performance.py # Performance analysis
│   ├── docs_qa.py     # RAG Q&A
│   └── common.py      # Shared utilities
└── workflow.py        # LangGraph builder
```

**Key components:**
1. **State**: TypedDict với user_id, mode, message, profile, assessments, gaps, plan, docs_results, citations
2. **Router**: Classify intent → coach_general | coach_skill | performance | docs_qa
3. **Coaching nodes**:
   - `fetch_user_data`: Load từ DB
   - `skill_resolver`: Parse skill từ message
   - `gap_analysis`: Calculate gaps
   - `course_selector`: Filter courses
   - `plan_builder`: Generate weekly plan
4. **Performance nodes**: Fetch stats + analyze
5. **Docs-QA nodes**: RAG retrieval + LLM synthesis + citations
6. **Workflow**: StateGraph với conditional routing

---

## 📋 Các Sprint tiếp theo

### Sprint 5: FastAPI Backend (TODO)
**Endpoints cần tạo:**
- `POST /chat/execute` - Main chat với LangGraph
- `GET /users/{id}` - User profile
- `GET /users/{id}/overview` - Performance overview
- `GET /skills/search?query=...` - Skill resolver
- `POST /documents/upload` - Upload file
- `POST /documents/ingest/{doc_id}` - Trigger ingest
- `POST /documents/query` - RAG search
- `GET /plans/{user_id}/active` - Active plan
- `POST /plans/{user_id}/confirm` - Save plan

**Security**: Model cố định ở server, không nhận từ client

### Sprint 6: Streamlit UI (TODO)
**Pages:**
1. **Chat**: Session state, mode selector, chat interface, citations display
2. **Dashboard**: User overview, scores cards, progress charts, enrollments table
3. **Documents**: Upload UI, search box, results với citations

### Sprint 7: Testing + LangSmith (TODO)
- Unit tests cho RAG, database services
- Integration tests cho LangGraph flows
- LangSmith tracing setup
- Coverage > 70%

### Sprint 8: Documentation + Git (TODO)
- Architecture diagram
- API documentation (OpenAPI)
- Deployment guide (Docker)
- Git init + push (safe, no secrets)

---

## 🧪 Cách test Sprint 3 (RAG)

```python
# Test script
from src.ai_coaching_bot.config import settings
from src.ai_coaching_bot.database.base import get_engine, get_session_maker
from src.ai_coaching_bot.rag.service import RAGService

# Setup
engine = get_engine(settings.database_url)
SessionLocal = get_session_maker(engine)
session = SessionLocal()

# Init RAG
rag = RAGService(session)

# Test upload + ingest
doc = rag.upload_document(
    file_path="docs/demo_docs/training_policy_2024.md",
    title="Chính sách đào tạo 2024"
)
print(f"Uploaded doc_id: {doc.id}")

chunks_count = rag.ingest_document(doc.id)
print(f"Ingested {chunks_count} chunks")

# Test query
results = rag.query_documents("ngân sách đào tạo", top_k=3)
for r in results:
    print(f"\nScore: {r['score']:.4f}")
    print(f"Citation: {r['citation']}")
    print(f"Text: {r['text'][:200]}...")
```

---

## 📦 Files đã tạo (tổng quan)

```
ai_coaching_bot/
├── .gitignore
├── .env.example
├── requirements.txt
├── setup_db.py
├── README.md
├── IMPLEMENTATION_PLAN.md
├── PROGRESS.md (this file)
├── src/ai_coaching_bot/
│   ├── __init__.py
│   ├── config.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── models.py (10 models)
│   │   └── seed.py
│   └── rag/
│       ├── __init__.py
│       ├── parser.py
│       ├── chunker.py
│       ├── embedder.py
│       ├── vector_store.py
│       └── service.py
├── docs/demo_docs/
│   ├── training_policy_2024.md
│   └── sql_best_practices.md
└── data/, faiss_index/, logs/ (empty, auto-created)
```

**Total files tạo**: 23 files
**Lines of code**: ~3000+ lines

---

## 🎯 Next Action

**Để tiếp tục Sprint 4 (LangGraph):**

1. Tạo `src/ai_coaching_bot/graph/state.py` - State schema
2. Tạo `src/ai_coaching_bot/graph/prompts.py` - System prompts
3. Tạo nodes trong `src/ai_coaching_bot/graph/nodes/`
4. Build workflow trong `src/ai_coaching_bot/graph/workflow.py`

Bạn có muốn tôi tiếp tục với Sprint 4 ngay bây giờ? (Y/N)
