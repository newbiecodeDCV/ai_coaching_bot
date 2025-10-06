"""
API Client - Wrapper cho FastAPI backend.
"""
import requests
from typing import Optional, Dict, List, Any
import streamlit as st


class APIClient:
    """Client để tương tác với FastAPI backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL của FastAPI backend
        """
        self.base_url = base_url
        self.session = requests.Session()
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Xử lý response từ API.
        
        Args:
            response: Response object từ requests
            
        Returns:
            Dict chứa data hoặc error
        """
        try:
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                return {"success": False, "error": error_data.get("detail", str(e))}
            except:
                return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    # ===== CHAT ENDPOINTS =====
    
    def chat_execute(self, user_id: str, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute chat workflow.
        
        Args:
            user_id: ID của user
            message: Message từ user
            session_id: Session ID (optional)
            
        Returns:
            Dict với response từ bot
        """
        url = f"{self.base_url}/chat/execute"
        payload = {
            "user_id": user_id,
            "message": message,
            "session_id": session_id
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=60)
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout - workflow took too long"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def chat_route(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Classify intent only.
        
        Args:
            user_id: ID của user
            message: Message từ user
            
        Returns:
            Dict với intent classification
        """
        url = f"{self.base_url}/chat/route"
        payload = {"user_id": user_id, "message": message}
        response = self.session.post(url, json=payload, timeout=30)
        return self._handle_response(response)
    
    # ===== USER ENDPOINTS =====
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile."""
        url = f"{self.base_url}/users/{user_id}"
        response = self.session.get(url)
        return self._handle_response(response)
    
    def get_user_overview(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user overview."""
        url = f"{self.base_url}/users/{user_id}/overview"
        response = self.session.get(url)
        return self._handle_response(response)
    
    def get_user_assessments(self, user_id: str, recent_days: int = 90) -> Dict[str, Any]:
        """Get user assessments."""
        url = f"{self.base_url}/users/{user_id}/assessments"
        params = {"recent_days": recent_days}
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def get_user_enrollments(self, user_id: str, status: Optional[str] = None) -> Dict[str, Any]:
        """Get user enrollments."""
        url = f"{self.base_url}/users/{user_id}/enrollments"
        params = {"status": status} if status else {}
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    # ===== SKILLS ENDPOINTS =====
    
    def list_skills(self, category: Optional[str] = None, search: Optional[str] = None, 
                   limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List all skills."""
        url = f"{self.base_url}/skills/"
        params = {"limit": limit, "offset": offset}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def get_skill(self, skill_id: str) -> Dict[str, Any]:
        """Get skill details."""
        url = f"{self.base_url}/skills/{skill_id}"
        response = self.session.get(url)
        return self._handle_response(response)
    
    def get_skill_with_stats(self, skill_id: str) -> Dict[str, Any]:
        """Get skill with statistics."""
        url = f"{self.base_url}/skills/{skill_id}/stats"
        response = self.session.get(url)
        return self._handle_response(response)
    
    def create_assessment(self, skill_id: str, user_id: str, score: int) -> Dict[str, Any]:
        """Create new assessment."""
        url = f"{self.base_url}/skills/{skill_id}/assess"
        payload = {"user_id": user_id, "score": score}
        response = self.session.post(url, json=payload)
        return self._handle_response(response)
    
    def get_skill_categories(self) -> Dict[str, Any]:
        """Get skill categories."""
        url = f"{self.base_url}/skills/categories/"
        response = self.session.get(url)
        return self._handle_response(response)
    
    def get_user_skills(self, user_id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Get user skills with assessment levels."""
        url = f"{self.base_url}/skills/user/{user_id}/"
        params = {"category": category} if category else {}
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    # ===== DOCUMENTS ENDPOINTS =====
    
    def list_documents(self, doc_type: Optional[str] = None, search: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List documents."""
        url = f"{self.base_url}/documents/"
        params = {"limit": limit, "offset": offset}
        if doc_type:
            params["doc_type"] = doc_type
        if search:
            params["search"] = search
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get document details."""
        url = f"{self.base_url}/documents/{document_id}"
        response = self.session.get(url)
        return self._handle_response(response)
    
    def upload_document(self, file, title: str, doc_type: str, 
                       description: Optional[str] = None, tags: Optional[str] = None) -> Dict[str, Any]:
        """Upload document."""
        url = f"{self.base_url}/documents/upload"
        files = {"file": file}
        data = {
            "title": title,
            "doc_type": doc_type,
            "description": description or "",
            "tags": tags or ""
        }
        response = self.session.post(url, files=files, data=data, timeout=120)
        return self._handle_response(response)
    
    def search_documents(self, query: str, top_k: int = 5, score_threshold: float = 0.3) -> Dict[str, Any]:
        """Search documents using vector search."""
        url = f"{self.base_url}/documents/search"
        payload = {
            "query": query,
            "top_k": top_k,
            "score_threshold": score_threshold
        }
        response = self.session.post(url, json=payload, timeout=30)
        return self._handle_response(response)
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete document."""
        url = f"{self.base_url}/documents/{document_id}"
        response = self.session.delete(url)
        return self._handle_response(response)
    
    def reindex_document(self, document_id: str) -> Dict[str, Any]:
        """Reindex document."""
        url = f"{self.base_url}/documents/{document_id}/reindex"
        response = self.session.put(url)
        return self._handle_response(response)
    
    def get_document_types(self) -> Dict[str, Any]:
        """Get document types."""
        url = f"{self.base_url}/documents/types/"
        response = self.session.get(url)
        return self._handle_response(response)
    
    # ===== PLANS ENDPOINTS =====
    
    def get_user_plans(self, user_id: str, status: Optional[str] = None,
                      limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get user learning plans."""
        url = f"{self.base_url}/plans/user/{user_id}"
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def get_plan_detail(self, plan_id: str) -> Dict[str, Any]:
        """Get plan details."""
        url = f"{self.base_url}/plans/{plan_id}"
        response = self.session.get(url)
        return self._handle_response(response)
    
    def create_plan(self, user_id: str, title: str, plan_data: Dict[str, Any],
                   description: Optional[str] = None) -> Dict[str, Any]:
        """Create new learning plan."""
        url = f"{self.base_url}/plans/user/{user_id}"
        payload = {
            "title": title,
            "description": description or "",
            "plan_data": plan_data
        }
        response = self.session.post(url, json=payload)
        return self._handle_response(response)
    
    def update_plan_status(self, plan_id: str, new_status: str) -> Dict[str, Any]:
        """Update plan status."""
        url = f"{self.base_url}/plans/{plan_id}/status"
        payload = {"new_status": new_status}
        response = self.session.put(url, json=payload)
        return self._handle_response(response)
    
    def delete_plan(self, plan_id: str) -> Dict[str, Any]:
        """Delete learning plan."""
        url = f"{self.base_url}/plans/{plan_id}"
        response = self.session.delete(url)
        return self._handle_response(response)
    
    def list_all_plans(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List all plans (admin)."""
        url = f"{self.base_url}/plans/"
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    # ===== HEALTH CHECK =====
    
    def health_check(self) -> Dict[str, Any]:
        """Health check."""
        url = f"{self.base_url.replace('/api/v1', '')}/health"
        try:
            response = self.session.get(url, timeout=5)
            return self._handle_response(response)
        except:
            return {"success": False, "error": "Cannot connect to backend"}


# Singleton instance
@st.cache_resource
def get_api_client() -> APIClient:
    """Get singleton API client instance."""
    return APIClient()