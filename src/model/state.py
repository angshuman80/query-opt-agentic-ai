from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime

# ---------- Core Input ----------
# This will be captured from system.query_history of Databricks
class QueryMetadata(BaseModel):
    user_name: str
    query_id: str
    workspace_name: str
    workspace_id: str
    tenant_id: str
    warehouse_type: str
    date_time: datetime

class QueryAnalysis(BaseModel):
    query_id: str
    query_text: str
    severity: str
    issues: List[str]
    root_cause: str
    cost_drivers: Dict[str, Any]

# ---------- Main LangGraph State ----------

class QueryOptimizerState(BaseModel):
    # Input
    query: QueryMetadata
    # Derived
    query_analysis: QueryAnalysis