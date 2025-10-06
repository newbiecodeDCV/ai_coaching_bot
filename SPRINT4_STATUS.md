# SPRINT 4 STATUS - LangGraph Workflow

## ✅ Đã hoàn thành

### 1. State Schema (`state.py`) ✅
- GraphState với TypedDict
- Tất cả fields cần thiết: user_id, mode, message, profile, assessments, enrollments, gaps, recommendations, plan, docs_results, answer, citations, error

### 2. Prompts (`prompts.py`) ✅
Đã tối ưu chi tiết với examples và guardrails:
- **ROUTER_PROMPT**: 4 categories với keywords và examples rõ ràng
- **SKILL_RESOLVER_PROMPT**: Level mapping (1-5), rules cụ thể, 3 examples
- **GAP_ANALYSIS_PROMPT**: Priority rules, framework phân tích
- **PLAN_BUILDER_PROMPT**: Weekly structure, planning rules, example output đầy đủ
- **PERFORMANCE_ANALYSIS_PROMPT**: 4 chiều phân tích, output structure
- **DOCS_QA_PROMPT**: Citation format, confidence scoring, 2 examples
- **SUMMARIZER_PROMPT**: Style guide, format template, tone examples
- **Utility functions**: format_skills_for_prompt, format_assessments_for_prompt, format_courses_for_prompt

## 🚧 Cần làm tiếp

### 3. Nodes Implementation
Tạo các file trong `src/ai_coaching_bot/graph/nodes/`:

#### `__init__.py`
```python
from .router import router_node
from .coaching import (
    fetch_user_data_node,
    skill_resolver_node,
    gap_analysis_node,
    course_selector_node,
    plan_builder_node
)
from .performance import performance_analysis_node
from .docs_qa import docs_qa_node
from .common import summarizer_node
```

#### `router.py`
- `router_node(state: GraphState) -> GraphState`
- Call LLM với ROUTER_PROMPT
- Parse JSON response
- Set state["mode"]

#### `coaching.py`
- `fetch_user_data_node`: Query DB cho profile, assessments, enrollments
- `skill_resolver_node`: LLM với SKILL_RESOLVER_PROMPT
- `gap_analysis_node`: LLM với GAP_ANALYSIS_PROMPT
- `course_selector_node`: Filter courses từ DB theo gaps
- `plan_builder_node`: LLM với PLAN_BUILDER_PROMPT

#### `performance.py`
- `performance_analysis_node`: LLM với PERFORMANCE_ANALYSIS_PROMPT
- Query DB cho recent data

#### `docs_qa.py`
- `docs_qa_node`: 
  - Call RAGService.query_documents()
  - Format context
  - LLM với DOCS_QA_PROMPT
  - Return với citations

#### `common.py`
- `summarizer_node`: LLM với SUMMARIZER_PROMPT
- Error handler
- Helper functions

### 4. Workflow Builder (`workflow.py`)
```python
from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes import *

def build_graph() -> CompiledGraph:
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("fetch_data", fetch_user_data_node)
    workflow.add_node("skill_resolver", skill_resolver_node)
    workflow.add_node("gap_analysis", gap_analysis_node)
    workflow.add_node("course_selector", course_selector_node)
    workflow.add_node("plan_builder", plan_builder_node)
    workflow.add_node("performance", performance_analysis_node)
    workflow.add_node("docs_qa", docs_qa_node)
    workflow.add_node("summarizer", summarizer_node)
    
    # Set entry
    workflow.set_entry_point("router")
    
    # Conditional edges
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
    
    # Coach flow edges
    workflow.add_edge("fetch_data", "skill_resolver")  # if coach_skill
    workflow.add_edge("skill_resolver", "gap_analysis")
    workflow.add_edge("gap_analysis", "course_selector")
    workflow.add_edge("course_selector", "plan_builder")
    workflow.add_edge("plan_builder", "summarizer")
    
    # Performance flow
    workflow.add_edge("performance", "summarizer")
    
    # Docs QA flow  
    workflow.add_edge("docs_qa", "summarizer")
    
    # End
    workflow.add_edge("summarizer", END)
    
    return workflow.compile()
```

## 📝 Implementation Checklist

- [x] State schema
- [x] Prompts với examples
- [x] Utility functions
- [ ] nodes/__init__.py
- [ ] nodes/router.py
- [ ] nodes/coaching.py (5 functions)
- [ ] nodes/performance.py
- [ ] nodes/docs_qa.py
- [ ] nodes/common.py
- [ ] workflow.py
- [ ] Integration test

## 🔧 Key Technical Points

### LLM Calling Pattern
```python
from langchain_openai import ChatOpenAI
from ..config import settings

llm = ChatOpenAI(
    model=settings.model_name,
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
    temperature=settings.temperature
)

response = llm.invoke(prompt)
parsed = json.loads(response.content)
```

### DB Access Pattern
```python
from ...database.base import get_engine, get_session_maker
from ...database.models import User, Skill, Assessment

engine = get_engine(settings.database_url)
SessionLocal = get_session_maker(engine)

with SessionLocal() as session:
    user = session.query(User).filter(User.id == user_id).first()
    assessments = session.query(Assessment).filter(
        Assessment.user_id == user_id
    ).all()
```

### Error Handling
```python
try:
    result = node_logic(state)
    return result
except Exception as e:
    state["error"] = str(e)
    state["answer"] = f"Xin lỗi, có lỗi xảy ra: {e}"
    return state
```

## 🎯 Next Steps

1. Implement router_node trước (đơn giản nhất)
2. Implement docs_qa_node (dùng RAGService đã có)
3. Implement fetch_user_data_node
4. Implement coaching nodes (5 nodes)
5. Implement performance_node
6. Implement summarizer_node
7. Build workflow.py
8. Integration test

Estimated time: 3-4 hours

Bạn muốn tôi tiếp tục implement các nodes không?
