# 🚀 HƯỚNG DẪN CHẠY AI COACHING BOT

## 📋 MỤC LỤC
1. [Kiểm tra môi trường](#1-kiểm-tra-môi-trường)
2. [Khởi động Backend (FastAPI)](#2-khởi-động-backend-fastapi)
3. [Khởi động Frontend (Streamlit)](#3-khởi-động-frontend-streamlit)
4. [Truy cập ứng dụng](#4-truy-cập-ứng-dụng)
5. [Hướng dẫn sử dụng](#5-hướng-dẫn-sử-dụng)
6. [Xử lý lỗi thường gặp](#6-xử-lý-lỗi-thường-gặp)

---

## 1. KIỂM TRA MÔI TRƯỜNG

### ✅ Bước 1.1: Kiểm tra Python và packages đã cài đặt

```powershell
# Kiểm tra phiên bản Python (cần >= 3.10)
python --version

# Kiểm tra các package chính đã cài chưa
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
python -c "import langchain; print('LangChain:', langchain.__version__)"
python -c "import langgraph; print('LangGraph:', langgraph.__version__)"
```

**Kết quả mong đợi:**
```
Python 3.10.x hoặc cao hơn
FastAPI: 0.115.4
Streamlit: 1.40.1
LangChain: 0.3.7
LangGraph: 0.2.45
```

### ✅ Bước 1.2: Kiểm tra file .env

```powershell
# Xem nội dung file .env
cat .env
```

**Đảm bảo có:**
- `OPENAI_API_KEY=sk-...` (API key hợp lệ)
- `OPENAI_BASE_URL=http://...` (URL đúng)
- `DATABASE_URL=sqlite:///./data/coaching_bot.db`

### ✅ Bước 1.3: Kiểm tra database đã có dữ liệu chưa

```powershell
# Kiểm tra file database tồn tại
ls data/coaching_bot.db

# Test kết nối database
python -c "
from sqlalchemy import create_engine, text
engine = create_engine('sqlite:///./data/coaching_bot.db')
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM users')).scalar()
    print(f'✅ Database OK - Có {result} users trong DB')
"
```

**Nếu chưa có database, chạy:**
```powershell
python setup_db.py
```

---

## 2. KHỞI ĐỘNG BACKEND (FastAPI)

### 🔥 Bước 2.1: Mở Terminal 1

```powershell
# Đảm bảo đang ở thư mục gốc của project
cd D:\ai_coaching_bot

# Khởi động FastAPI backend
uvicorn src.ai_coaching_bot.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Output mong đợi:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database tables created successfully
INFO:     Application startup complete.
```

### ✅ Bước 2.2: Kiểm tra Backend đang chạy

**Mở Terminal 2 (PowerShell khác):**

```powershell
# Test health endpoint
curl http://localhost:8000/health

# Hoặc dùng Python
python -c "
import requests
response = requests.get('http://localhost:8000/health')
print(response.json())
"
```

**Kết quả mong đợi:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-06T04:56:30.000Z",
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "api": "healthy"
  }
}
```

### 🌐 Bước 2.3: Truy cập API Documentation

Mở trình duyệt:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 3. KHỞI ĐỘNG FRONTEND (Streamlit)

### 🔥 Bước 3.1: Mở Terminal 3 (Terminal mới)

```powershell
# Đảm bảo đang ở thư mục gốc
cd D:\ai_coaching_bot

# Khởi động Streamlit UI
streamlit run streamlit_ui/Home.py --server.port 8501
```

**Output mong đợi:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### ✅ Bước 3.2: Kiểm tra kết nối Backend

Streamlit sẽ tự động kiểm tra kết nối với FastAPI backend và hiển thị status ở sidebar.

**Nếu thấy:**
- ✅ **Backend: Connected** → OK!
- ❌ **Backend: Disconnected** → Kiểm tra lại Terminal 1 (FastAPI có đang chạy không?)

---

## 4. TRUY CẬP ỨNG DỤNG

### 🌐 URLs chính:

| Dịch vụ | URL | Mô tả |
|---------|-----|-------|
| **Streamlit UI** | http://localhost:8501 | Giao diện người dùng |
| **FastAPI Backend** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **Health Check** | http://localhost:8000/health | Kiểm tra trạng thái |

### 📱 Các trang trong Streamlit:

1. **🏠 Home** - Dashboard tổng quan
   - User metrics
   - Skill gaps
   - Recent assessments
   - Active enrollments

2. **💬 Chat** - Trò chuyện với AI Coach
   - Coaching mode
   - Performance analysis
   - Docs Q&A

3. **👤 Profile** - Quản lý hồ sơ
   - User info
   - Skills management
   - Create assessments
   - Performance analytics

4. **📋 Plans** - Learning plans
   - View all plans
   - Plan details
   - Status management

5. **📚 Documents** - Document library
   - Upload documents
   - Vector search (RAG)
   - Document management

---

## 5. HƯỚNG DẪN SỬ DỤNG

### 🎯 Use Case 1: Chat với AI Coach

**Bước 1:** Vào trang **Chat** (từ sidebar)

**Bước 2:** Chọn user từ dropdown (ví dụ: "Nguyễn Văn A")

**Bước 3:** Nhập câu hỏi, ví dụ:
- "Tôi muốn học Python từ đầu"
- "Phân tích hiệu suất học tập của tôi"
- "Tạo learning plan cho tôi về SQL"

**Bước 4:** Đợi AI xử lý (5-10 giây)

**Bước 5:** Xem kết quả:
- Response từ AI
- Metadata (mode, citations)
- Learning plan (nếu có)

### 🎯 Use Case 2: Upload và Query Document

**Bước 1:** Vào trang **Documents**

**Bước 2:** Tab "📤 Upload" → Chọn file (PDF/TXT/MD)

**Bước 3:** Nhập title → Click "Upload & Index"

**Bước 4:** Đợi indexing hoàn tất

**Bước 5:** Tab "🔍 Search" → Nhập query → Click Search

**Kết quả:** Các đoạn văn bản liên quan với score và citation

### 🎯 Use Case 3: Tạo Assessment cho Skill

**Bước 1:** Vào trang **Profile**

**Bước 2:** Chọn user

**Bước 3:** Tab "Skills Catalog"

**Bước 4:** Tìm skill (ví dụ: "SQL")

**Bước 5:** Click "Assess" → Nhập score (0-100)

**Bước 6:** Submit → Level sẽ được cập nhật tự động

### 🎯 Use Case 4: Xem Learning Plan

**Bước 1:** Vào trang **Plans**

**Bước 2:** Chọn user

**Bước 3:** Xem danh sách plans với status

**Bước 4:** Click "View Details" để xem chi tiết:
- Weekly breakdown
- Courses
- Milestones
- KPIs

**Bước 5:** Pause/Resume/Delete plan nếu cần

---

## 6. XỬ LÝ LỖI THƯỜNG GẶP

### ❌ Lỗi: "Module not found"

**Nguyên nhân:** Chưa cài đặt đủ packages

**Giải pháp:**
```powershell
pip install -r requirements.txt
```

### ❌ Lỗi: "Database not found"

**Nguyên nhân:** Chưa chạy setup_db.py

**Giải pháp:**
```powershell
python setup_db.py
```

### ❌ Lỗi: "Backend disconnected" trong Streamlit

**Nguyên nhân:** FastAPI chưa chạy hoặc sai port

**Giải pháp:**
1. Kiểm tra Terminal 1 có FastAPI đang chạy không
2. Kiểm tra http://localhost:8000/health
3. Restart FastAPI nếu cần

### ❌ Lỗi: "OpenAI API Error"

**Nguyên nhân:** API key sai hoặc base URL không đúng

**Giải pháp:**
1. Kiểm tra file `.env`:
   ```bash
   OPENAI_API_KEY=sk-...
   OPENAI_BASE_URL=http://...
   ```
2. Test API key:
   ```powershell
   python -c "
   from openai import OpenAI
   import os
   from dotenv import load_dotenv
   load_dotenv()
   client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), base_url=os.getenv('OPENAI_BASE_URL'))
   response = client.chat.completions.create(
       model='gpt-4o-mini',
       messages=[{'role': 'user', 'content': 'Hello'}]
   )
   print('✅ OpenAI API OK')
   "
   ```

### ❌ Lỗi: Port already in use

**Lỗi:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Giải pháp 1:** Tắt process đang dùng port
```powershell
# Tìm process đang dùng port 8000
netstat -ano | findstr :8000

# Kill process (thay <PID> bằng số PID tìm được)
taskkill /PID <PID> /F
```

**Giải pháp 2:** Dùng port khác
```powershell
# FastAPI dùng port 8001
uvicorn src.ai_coaching_bot.api.main:app --reload --port 8001

# Streamlit dùng port 8502
streamlit run streamlit_ui/Home.py --server.port 8502
```

### ❌ Lỗi: LangGraph workflow failed

**Nguyên nhân:** Database thiếu dữ liệu hoặc LLM error

**Giải pháp:**
1. Kiểm tra database có dữ liệu:
   ```powershell
   python -c "
   from sqlalchemy import create_engine, text
   engine = create_engine('sqlite:///./data/coaching_bot.db')
   with engine.connect() as conn:
       print('Users:', conn.execute(text('SELECT COUNT(*) FROM users')).scalar())
       print('Skills:', conn.execute(text('SELECT COUNT(*) FROM skills')).scalar())
       print('Courses:', conn.execute(text('SELECT COUNT(*) FROM courses')).scalar())
   "
   ```
2. Nếu thiếu dữ liệu → Chạy lại `python setup_db.py`
3. Kiểm tra log trong Terminal 1 (FastAPI)

---

## 📊 KIỂM TRA HỆ THỐNG HOẠT ĐỘNG ĐÚNG

### ✅ Checklist toàn diện:

```powershell
# 1. Check Python version
python --version

# 2. Check database
ls data/coaching_bot.db

# 3. Check backend health
curl http://localhost:8000/health

# 4. Check Streamlit running
curl http://localhost:8501

# 5. Test chat API
python -c "
import requests
response = requests.post(
    'http://localhost:8000/api/v1/chat/execute',
    json={'user_id': 'user_001', 'message': 'Hello'}
)
print('Status:', response.status_code)
print('Response:', response.json())
"
```

**Nếu tất cả đều OK → Hệ thống đã sẵn sàng! 🎉**

---

## 🎓 DEMO WORKFLOWS

### Demo 1: General Coaching
```
User: "Tôi là Data Analyst level 2, muốn nâng cao kỹ năng"
→ AI sẽ:
  1. Phân tích gaps dựa trên role
  2. Đề xuất courses
  3. Tạo learning plan 4-8 tuần
```

### Demo 2: Skill-Specific Coaching
```
User: "Tôi cần học Python cơ bản trong 3 tháng"
→ AI sẽ:
  1. Resolve skill "Python"
  2. Tìm gaps (hiện tại vs target level 2)
  3. Filter courses phù hợp 3 tháng
  4. Tạo weekly plan
```

### Demo 3: Performance Analysis
```
User: "Phân tích hiệu suất học tập của tôi"
→ AI sẽ:
  1. Fetch assessments, enrollments
  2. Tính metrics (avg score, completion rate)
  3. Identify strengths vs improvements
  4. Đưa ra recommendations
```

### Demo 4: Document Q&A
```
User: "Ngân sách đào tạo năm 2024 là bao nhiêu?"
→ AI sẽ:
  1. RAG search trong documents
  2. Retrieve relevant chunks
  3. Synthesize answer
  4. Provide citations
```

---

## 🛑 TẮT ỨNG DỤNG

### Tắt an toàn:

**Terminal 1 (FastAPI):** 
```
Nhấn Ctrl+C
```

**Terminal 3 (Streamlit):**
```
Nhấn Ctrl+C
```

### Cleanup (nếu cần):
```powershell
# Xóa cache
rm -r __pycache__
rm -r .streamlit/cache

# Xóa FAISS index (nếu muốn reset)
rm -r data/faiss_index/
```

---

## 📞 HỖ TRỢ

**Nếu gặp vấn đề:**
1. Đọc lại phần "Xử lý lỗi thường gặp"
2. Kiểm tra logs trong Terminal
3. Kiểm tra API docs: http://localhost:8000/docs
4. Test từng component riêng (database, API, Streamlit)

**Log files:**
- FastAPI logs: Terminal 1 output
- Streamlit logs: Terminal 3 output

---

## 🎉 HOÀN THÀNH!

Bây giờ bạn đã có hệ thống AI Coaching Bot chạy hoàn chỉnh với:
- ✅ FastAPI Backend (24 endpoints)
- ✅ LangGraph Workflow (9 nodes)
- ✅ RAG System (FAISS + OpenAI)
- ✅ Streamlit UI (5 pages)
- ✅ SQLite Database với seed data

**Happy Coding! 🚀**
