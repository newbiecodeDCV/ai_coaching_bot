"""
Documents router - Document upload, manage và search endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database.models import Document
from ..schemas import DocumentResponse, DocumentSearchRequest, DocumentSearchResponse, ErrorResponse
from ..dependencies import get_db
from ...rag.rag_service import RAGService
from datetime import datetime
import uuid
import os
import shutil

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/",
           response_model=List[DocumentResponse],
           summary="Lấy danh sách documents",
           description="Endpoint để lấy danh sách tất cả documents trong hệ thống.")
async def list_documents(
    doc_type: Optional[str] = Query(None, description="Filter theo doc_type"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo title hoặc description"),
    limit: int = Query(100, ge=1, le=500, description="Giới hạn số kết quả"),
    offset: int = Query(0, ge=0, description="Offset cho pagination"),
    db: Session = Depends(get_db)
) -> List[DocumentResponse]:
    """
    Lấy danh sách documents với filters và pagination.
    
    Args:
        doc_type: Filter theo document type
        search: Tìm kiếm trong title và description
        limit: Giới hạn số kết quả
        offset: Offset cho pagination
        db: Database session
        
    Returns:
        List của DocumentResponse
    """
    try:
        # Build query
        query = db.query(Document)
        
        # Apply filters
        if doc_type:
            query = query.filter(Document.doc_type == doc_type)
        
        if search:
            query = query.filter(
                (Document.title.ilike(f"%{search}%")) |
                (Document.description.ilike(f"%{search}%"))
            )
        
        # Apply pagination
        query = query.offset(offset).limit(limit).order_by(Document.created_at.desc())
        
        documents = query.all()
        
        return [
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                description=doc.description,
                doc_type=doc.doc_type,
                file_path=doc.file_path,
                file_size=doc.file_size,
                is_indexed=doc.is_indexed,
                tags=doc.tags,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
            for doc in documents
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}",
           response_model=DocumentResponse,
           summary="Lấy thông tin document",
           description="Endpoint để lấy thông tin chi tiết của document theo ID.")
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
) -> DocumentResponse:
    """
    Lấy thông tin chi tiết của document.
    
    Args:
        document_id: ID của document
        db: Database session
        
    Returns:
        DocumentResponse với thông tin chi tiết
        
    Raises:
        HTTPException: 404 nếu document không tồn tại
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} không tồn tại"
            )
        
        return DocumentResponse(
            id=document.id,
            title=document.title,
            description=document.description,
            doc_type=document.doc_type,
            file_path=document.file_path,
            file_size=document.file_size,
            is_indexed=document.is_indexed,
            tags=document.tags,
            created_at=document.created_at,
            updated_at=document.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload",
            response_model=DocumentResponse,
            summary="Upload document mới",
            description="Endpoint để upload document và tự động index vào vector store.")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    doc_type: str = Form(...),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db)
) -> DocumentResponse:
    """
    Upload document mới và index vào vector store.
    
    Args:
        file: File upload
        title: Tiêu đề document
        description: Mô tả document
        doc_type: Loại document
        tags: Tags (comma-separated)
        db: Database session
        
    Returns:
        DocumentResponse với thông tin document mới
        
    Raises:
        HTTPException: 400 cho file không hợp lệ, 500 cho lỗi server
    """
    try:
        # Validate file type
        allowed_types = ['.pdf', '.txt', '.md', '.docx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} không được hỗ trợ. Chỉ hỗ trợ: {', '.join(allowed_types)}"
            )
        
        # Validate file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size không được vượt quá 10MB"
            )
        
        # Generate unique filename
        document_id = str(uuid.uuid4())
        filename = f"{document_id}{file_ext}"
        
        # Create uploads directory if not exists
        uploads_dir = "data/uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(uploads_dir, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse tags
        tags_list = []
        if tags:
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Create document record
        new_document = Document(
            id=document_id,
            title=title,
            description=description or "",
            doc_type=doc_type,
            file_path=file_path,
            file_size=file.size,
            is_indexed=False,
            tags=tags_list,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        
        # Index document in background
        try:
            rag_service = RAGService()
            success = await rag_service.ingest_document(file_path, document_id)
            
            if success:
                new_document.is_indexed = True
                db.commit()
        except Exception as e:
            # Log error but don't fail the upload
            print(f"Warning: Failed to index document {document_id}: {e}")
        
        return DocumentResponse(
            id=new_document.id,
            title=new_document.title,
            description=new_document.description,
            doc_type=new_document.doc_type,
            file_path=new_document.file_path,
            file_size=new_document.file_size,
            is_indexed=new_document.is_indexed,
            tags=new_document.tags,
            created_at=new_document.created_at,
            updated_at=new_document.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if database operation failed
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search",
            response_model=DocumentSearchResponse,
            summary="Tìm kiếm documents",
            description="Endpoint để tìm kiếm nội dung trong documents sử dụng vector search.")
async def search_documents(
    request: DocumentSearchRequest,
    db: Session = Depends(get_db)
) -> DocumentSearchResponse:
    """
    Tìm kiếm documents sử dụng vector search.
    
    Args:
        request: DocumentSearchRequest với query và filters
        db: Database session
        
    Returns:
        DocumentSearchResponse với kết quả tìm kiếm
        
    Raises:
        HTTPException: 400 cho query không hợp lệ, 500 cho lỗi server
    """
    try:
        # Validate query
        if not request.query or len(request.query.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Query phải có ít nhất 3 ký tự"
            )
        
        # Use RAG service to search
        rag_service = RAGService()
        
        search_results = await rag_service.query(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold
        )
        
        # Extract document IDs from results
        doc_ids = []
        results_data = []
        
        for result in search_results:
            doc_id = result.get('document_id')
            if doc_id:
                doc_ids.append(doc_id)
            
            results_data.append({
                "content": result.get('content', ''),
                "score": result.get('score', 0.0),
                "document_id": doc_id,
                "chunk_index": result.get('chunk_index', 0)
            })
        
        # Get document metadata
        documents = []
        if doc_ids:
            db_documents = db.query(Document).filter(Document.id.in_(doc_ids)).all()
            document_lookup = {doc.id: doc for doc in db_documents}
            
            for doc_id in set(doc_ids):
                if doc_id in document_lookup:
                    doc = document_lookup[doc_id]
                    documents.append({
                        "id": doc.id,
                        "title": doc.title,
                        "description": doc.description,
                        "doc_type": doc.doc_type,
                        "tags": doc.tags
                    })
        
        return DocumentSearchResponse(
            query=request.query,
            total_results=len(results_data),
            results=results_data,
            documents=documents,
            success=True,
            message=f"Tìm thấy {len(results_data)} kết quả"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}",
              response_model=dict,
              summary="Xóa document",
              description="Endpoint để xóa document và dọn dẹp các file liên quan.")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Xóa document và dọn dẹp files.
    
    Args:
        document_id: ID của document cần xóa
        db: Database session
        
    Returns:
        Dict với thông báo thành công
        
    Raises:
        HTTPException: 404 nếu document không tồn tại
    """
    try:
        # Find document
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} không tồn tại"
            )
        
        # Delete physical file if exists
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Remove from vector store
        try:
            rag_service = RAGService()
            await rag_service.delete_document(document_id)
        except Exception as e:
            # Log but don't fail the deletion
            print(f"Warning: Failed to remove document from vector store: {e}")
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {
            "success": True,
            "message": f"Document {document_id} đã được xóa thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{document_id}/reindex",
           response_model=dict,
           summary="Reindex document",
           description="Endpoint để reindex document vào vector store.")
async def reindex_document(
    document_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Reindex document vào vector store.
    
    Args:
        document_id: ID của document cần reindex
        db: Database session
        
    Returns:
        Dict với kết quả reindex
        
    Raises:
        HTTPException: 404 nếu document không tồn tại
    """
    try:
        # Find document
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} không tồn tại"
            )
        
        # Check if file exists
        if not document.file_path or not os.path.exists(document.file_path):
            raise HTTPException(
                status_code=400,
                detail=f"File của document {document_id} không tồn tại"
            )
        
        # Remove old index first
        try:
            rag_service = RAGService()
            await rag_service.delete_document(document_id)
        except Exception:
            pass  # Ignore if not indexed yet
        
        # Reindex document
        rag_service = RAGService()
        success = await rag_service.ingest_document(document.file_path, document_id)
        
        # Update database
        document.is_indexed = success
        document.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": success,
            "message": f"Document {document_id} {'đã được' if success else 'không thể'} reindex"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types/",
           response_model=List[dict],
           summary="Lấy document types",
           description="Endpoint để lấy danh sách các document types và số lượng.")
async def get_document_types(
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Lấy danh sách document types với counts.
    
    Args:
        db: Database session
        
    Returns:
        List document types với counts
    """
    try:
        from sqlalchemy import func
        
        types = db.query(
            Document.doc_type,
            func.count(Document.id).label('count')
        ).group_by(Document.doc_type).all()
        
        result = []
        for doc_type, count in types:
            result.append({
                "doc_type": doc_type,
                "count": count
            })
        
        return sorted(result, key=lambda x: x['count'], reverse=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
