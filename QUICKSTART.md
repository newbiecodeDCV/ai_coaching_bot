# ⚡ QUICK START - AI COACHING BOT

## 🚀 CHẠY NGAY (3 BƯỚC)

### ✅ Kiểm tra nhanh môi trường

```powershell
# Kiểm tra Python
python --version

# Kiểm tra database
ls data/coaching_bot.db
```

---

## 📝 BƯỚC 1: KHỞI ĐỘNG BACKEND (FastAPI)

**Mở Terminal/PowerShell thứ nhất:**

```powershell
uvicorn src.ai_coaching_bot.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Chờ thấy:**
```
INFO:     Application startup complete.
```

**Test nhanh (Terminal khác):**
```powershell
curl http://localhost:8000/health
```

---

## 🎨 BƯỚC 2: KHỞI ĐỘNG FRONTEND (Streamlit)

**Mở Terminal/PowerShell thứ hai:**

```powershell
streamlit run streamlit_ui/Home.py --server.port 8501
```

**Chờ thấy:**
```
Local URL: http://localhost:8501
```

---

## 🌐 BƯỚC 3: MỞ TRÌNH DUYỆT

### Truy cập các URL:

| Ứng dụng | URL |
|----------|-----|
| **🎨 Streamlit UI** | http://localhost:8501 |
| **📚 API Docs** | http://localhost:8000/docs |
| **❤️ Health Check** | http://localhost:8000/health |

---

## 🎯 THỬ NGHIỆM NHANH

### Test 1: Chat với AI Coach

1. Vào **Streamlit**: http://localhost:8501
2. Sidebar: Chọn "💬 Chat"
3. Chọn user: "Nguyễn Văn A"
4. Nhập: "Tôi muốn học Python"
5. Xem kết quả AI response

### Test 2: Xem Dashboard

1. Trang Home tự động hiển thị
2. Xem metrics, skill gaps, enrollments

### Test 3: Kiểm tra API

1. Vào: http://localhost:8000/docs
2. Thử endpoint: **GET** `/api/v1/users/user_001`
3. Click "Try it out" → "Execute"

---

## 🛑 TẮT ỨNG DỤNG

```
Terminal 1 (FastAPI): Ctrl+C
Terminal 2 (Streamlit): Ctrl+C
```

---

## ❌ LỖI THƯỜNG GẶP

### Port đã được sử dụng?

```powershell
# Tìm process đang dùng port 8000
netstat -ano | findstr :8000

# Kill process (thay <PID>)
taskkill /PID <PID> /F
```

### Backend không kết nối?

1. Kiểm tra Terminal 1 có lỗi không
2. Test: `curl http://localhost:8000/health`
3. Restart FastAPI

---

## 📖 TÀI LIỆU CHI TIẾT

- **Full Guide**: `HUONG_DAN_CHAY.md`
- **Architecture**: `FINAL_README.md`
- **API Reference**: http://localhost:8000/docs

---

## ✅ HOÀN TẤT!

Bạn đã chạy thành công:
- ✅ FastAPI Backend (Port 8000)
- ✅ Streamlit UI (Port 8501)
- ✅ Database với seed data
- ✅ LangGraph workflow
- ✅ RAG system

**🎉 Enjoy your AI Coaching Bot!**
