# KẾ HOẠCH TRIỂN KHAI CHI TIẾT

## ✅ Đã hoàn thành

### Sprint 0: Setup môi trường
- ✅ `.gitignore` với rules đầy đủ
- ✅ `.env.example` template (không chứa secret)
- ✅ `requirements.txt` với dependencies
- ✅ Cấu trúc thư mục chuẩn

### Sprint 1: Database
- ✅ SQLAlchemy models (Users, Skills, Courses, Assessments, Enrollments, Plans, Documents)
- ✅ Seed data script với 10 skills, 10 courses, 3 users demo
- ✅ `setup_db.py` script

### Sprint 2: Config
- ✅ `config.py` với Pydantic settings
- ✅ Environment loader

## 🔨 Cần triển khai tiếp

### Sprint 3: RAG Components

**File cần tạo:**

```
src/ai_coaching_bot/rag/
├── __init__.py
├── parser.py          # PDF/MD parser
├── chunker.py         # Text chunking (800-1200 tokens)
├── embedder.py        # OpenAI embedding wrapper
├── vector_store.py    # FAISS manager
└── service.py         # Upload/ingest/query logic
```

**Chức năng:**
1. **Parser** (`parser.py`):
   - `parse_pdf(file_path)` → text + metadata (pages)
   - `parse_markdown(file_path)` → text

2. **Chunker** (`chunker.py`):
   - `chunk_text(text, chunk_size=1000, overlap=150)` → List[chunks]
   - Metadata: document_id, chunk_index, page

3. **Embedder** (`embedder.py`):
   - `embed_texts(texts: List[str])` → np.array
   - Cache embedding theo file hash

4. **VectorStore** (`vector_store.py`):
   - `create_index()` → FAISS index
   - `add_documents(doc_id, chunks, embeddings)`
   - `search(query, top_k=5)` → List[chunks with scores]

5. **Service** (`service.py`):
   - `upload_document(file, skill_id=None)` → Document
   - `ingest_document(doc_id)` → chunk + embed + index
   - `query_documents(query, skill_id=None, top_k=5)` → Results with citations

---

### Sprint 4: LangGraph Workflow

**File cần tạo:**

```
src/ai_coaching_bot/graph/
├── __init__.py
├── state.py           # State schema (Pydantic)
├── prompts.py         # System prompts cho từng node
├── nodes/
│   ├── __init__.py
│   ├── router.py      # Intent classification
│   ├── coaching.py    # General + skill-specific coaching
│   ├── performance.py # Performance analysis
│   ├── docs_qa.py     # RAG-based Q&A
│   └── common.py      # Shared nodes (summarizer, etc.)
└── workflow.py        # LangGraph workflow builder
```

**State Schema** (`state.py`):
```python
class GraphState(TypedDict):
    user_id: str
    mode: str  # coach_general | coach_skill | performance | docs_qa
    message: str
    user_profile: dict
    assessments: List[dict]
    enrollments: List[dict]
    skill_query: Optional[str]
    target_level: Optional[int]
    gaps: List[dict]
    recommendations: List[dict]
    plan: Optional[dict]
    docs_results: List[dict]
    answer: str
    citations: List[str]
```

**Nodes chi tiết:**

1. **Router** (`router.py`):
   - Input: message
   - LLM classification hoặc keyword matching
   - Output: mode (coach_general | coach_skill | performance | docs_qa)

2. **Coaching** (`coaching.py`):
   - `fetch_user_data`: lấy profile, assessments, enrollments từ DB
   - `skill_resolver`: parse skill từ message, map với DB synonyms
   - `infer_current_level`: từ assessments hoặc hỏi user
   - `gap_analysis`: expected vs current, tính gap
   - `course_selector`: filter courses theo skill/level/budget
   - `plan_builder`: tạo weekly plan
   - `save_plan`: ghi vào DB

3. **Performance** (`performance.py`):
   - `fetch_user_stats`: lấy assessments, enrollments theo user_id
   - `analyze_performance`: tổng hợp điểm, progress, gaps
   - `generate_summary`: format response + next actions

4. **Docs-QA** (`docs_qa.py`):
   - `retrieve_docs`: gọi RAG service
   - `generate_answer`: LLM synthesis với context
   - `format_citations`: [doc:title#page]

5. **Common** (`common.py`):
   - `summarizer`: tóm tắt final response
   - `error_handler`: xử lý lỗi gracefully

**Workflow** (`workflow.py`):
```python
def build_graph():
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("fetch_data", fetch_user_data_node)
    workflow.add_node("coaching", coaching_node)
    workflow.add_node("performance", performance_node)
    workflow.add_node("docs_qa", docs_qa_node)
    workflow.add_node("summarizer", summarizer_node)
    
    # Add edges với conditional routing
    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        lambda state: state["mode"],
        {
            "coach_general": "fetch_data",
            "coach_skill": "fetch_data",
            "performance": "fetch_data",
            "docs_qa": "docs_qa"
        }
    )
    # ... thêm edges
    
    return workflow.compile()
```

---

### Sprint 5: FastAPI Backend

**File cần tạo:**

```
src/ai_coaching_bot/api/
├── __init__.py
├── main.py            # FastAPI app
├── routers/
│   ├── __init__.py
│   ├── chat.py        # Chat endpoints
│   ├── users.py       # User endpoints
│   ├── skills.py      # Skills endpoints
│   ├── documents.py   # Documents endpoints
│   └── plans.py       # Plans endpoints
├── schemas.py         # Pydantic request/response models
└── dependencies.py    # DB session, auth (future)
```

**Endpoints chi tiết:**

#### `/chat` (chat.py)
```python
POST /chat/execute
Body: {user_id, message, session_id?}
Response: {answer, citations?, plan?, trace_id?}
```

#### `/users` (users.py)
```python
GET /users/{id}
Response: User profile

GET /users/{id}/overview
Response: {
  assessments: [...],
  enrollments: [...],
  gaps: [...],
  active_plan: {...}
}
```

#### `/skills` (skills.py)
```python
GET /skills/search?query=...
Response: [{id, name, synonyms, confidence}]

GET /skills
Response: List all skills
```

#### `/documents` (documents.py)
```python
POST /documents/upload
Body: multipart/form-data (file, skill_id?)
Response: {document_id, title}

POST /documents/ingest/{doc_id}
Response: {status, chunks_count}

POST /documents/query
Body: {query, skill_id?, top_k?}
Response: {results: [{text, score, document, page}]}

GET /documents
Response: List documents
```

#### `/plans` (plans.py)
```python
GET /plans/{user_id}/active
Response: Active learning plan

POST /plans/{user_id}/confirm
Body: {title, items: [{week_no, target, course_id, kpi}]}
Response: {plan_id}
```

**Security:**
- Model name/temperature cố định ở server (không nhận từ request)
- Rate limiting (future)
- CORS setup cho Streamlit

---

### Sprint 6: Streamlit UI

**File cần tạo:**

```
streamlit_app.py       # Main entry
pages/
├── 1_💬_Chat.py
├── 2_📊_Dashboard.py
└── 3_📚_Documents.py
```

**1_💬_Chat.py:**
- Session state management (user_id, messages history)
- Mode selector: Auto / Coach / Performance / Docs
- Chat input → POST /chat/execute → hiển thị response
- Hiển thị citations nếu có
- Nút "Xác nhận kế hoạch" nếu bot đề xuất plan

**2_📊_Dashboard.py:**
- GET /users/{id}/overview
- Cards: điểm trung bình, khóa đang học, gaps
- Table: enrollments với progress bar
- Chart: skill levels (radar chart)
- Timeline: milestones sắp tới

**3_📚_Documents.py:**
- Upload file → POST /documents/upload → POST /documents/ingest
- Search box → POST /documents/query
- Results table với citations, link mở doc
- Filter theo skill

---

### Sprint 7: Testing

**File cần tạo:**

```
tests/
├── __init__.py
├── test_database.py       # ORM tests
├── test_rag.py            # RAG components tests
├── test_graph.py          # LangGraph nodes tests
├── test_api.py            # FastAPI endpoints tests (pytest-httpx)
└── integration/
    └── test_flows.py      # End-to-end flows
```

**Test cases quan trọng:**
1. Skill resolver: "tôi cần học SQL" → skill_id=sql
2. Coaching flow: user_001 + "học Python lên level 3" → plan hợp lý
3. Performance: user_001 hỏi điểm → trả về assessments đúng
4. RAG: query "policy đào tạo" → có citations
5. API: POST /chat/execute với mock LLM

**LangSmith:**
- Setup tracing env
- Verify trace_id trong response
- Monitor latency và token usage

---

### Sprint 8: Documentation & Deployment

**Docs cần tạo:**

```
docs/
├── architecture.md        # Sơ đồ chi tiết
├── api_reference.md       # OpenAPI spec
├── deployment.md          # Docker, env setup
└── troubleshooting.md     # Common issues
```

**Deployment checklist:**
- [ ] Dockerfile cho FastAPI
- [ ] Dockerfile cho Streamlit
- [ ] docker-compose.yml
- [ ] Env template cho production
- [ ] Health check endpoints
- [ ] Logging aggregation

---

## 🎯 Tiêu chí nghiệm thu từng Sprint

### Sprint 3 (RAG):
- ✅ Upload PDF 1MB → ingest < 10s
- ✅ Query "SQL best practices" → top-5 results có citations
- ✅ Embedding cache hoạt động (reupload nhanh hơn)

### Sprint 4 (LangGraph):
- ✅ Router phân loại đúng ≥90% test cases
- ✅ Coaching flow: "học SQL" → plan với courses cụ thể
- ✅ Performance flow: user_id → điểm + gaps
- ✅ Docs-QA flow: câu hỏi → answer + citations

### Sprint 5 (FastAPI):
- ✅ All endpoints return 200 với valid input
- ✅ POST /chat/execute < 4s (P95)
- ✅ OpenAPI docs tự động (/docs)
- ✅ User không thể override model name

### Sprint 6 (Streamlit):
- ✅ Chat UI responsive, messages render đúng
- ✅ Dashboard load data từ API
- ✅ Upload document → ingest → query workflow

### Sprint 7 (Testing):
- ✅ Unit test coverage > 70%
- ✅ Integration tests pass
- ✅ LangSmith trace visible

### Sprint 8 (Docs):
- ✅ README đầy đủ (setup, usage, architecture)
- ✅ API docs (OpenAPI + examples)
- ✅ Deployment guide (Docker)

---

## 🚀 Lệnh chạy (sau khi hoàn thiện)

```bash
# Setup
python setup_db.py

# Run FastAPI
uvicorn src.ai_coaching_bot.api.main:app --reload --port 8000

# Run Streamlit (tab khác)
streamlit run streamlit_app.py --server.port 8501

# Tests
pytest tests/ -v --cov=src
```

---

## 📌 Lưu ý quan trọng

1. **Không commit secret**: luôn check `.env` trong `.gitignore`
2. **Docstring tiếng Việt**: mọi function đều phải có
3. **Type hints**: sử dụng đầy đủ
4. **Error handling**: wrap LLM calls với try-except + tenacity retry
5. **Logging**: log INFO cho actions, ERROR cho failures
6. **Model cố định**: không cho user gửi `model` param từ frontend

---

## 🔄 Iteration sau v1

- [ ] Multi-user auth (JWT)
- [ ] Real-time collaboration
- [ ] Email notifications cho milestones
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Integration với LMS/HRIS
