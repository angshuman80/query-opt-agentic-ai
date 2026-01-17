from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class QueryHistoryRecord(BaseModel):
    query_id: str
    query_text: str
    warehouse_name: str
    execution_time_ms: int
    bytes_scanned: int
    rows_produced: int
    start_time: datetime

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# ---- Operator Models ----

class TableScanOperator(BaseModel):
    operator_type: Literal["TableScan"]
    table_name: str
    bytes_scanned: int = Field(..., ge=0)
    partition_pruning: Literal["NONE", "PARTIAL", "FULL"]


class HashJoinOperator(BaseModel):
    operator_type: Literal["HashJoin"]
    join_type: Literal["INNER", "LEFT", "RIGHT", "FULL"]
    left_rows: int = Field(..., ge=0)
    right_rows: int = Field(..., ge=0)


# ---- Union of Operators ----

QueryOperator = TableScanOperator | HashJoinOperator


# ---- Query Profile Root ----

class QueryProfile(BaseModel):
    query_id: str
    operators: List[QueryOperator]
    total_elapsed_time_ms: int = Field(..., ge=0)

class TableStorage(BaseModel):
    table_name: str
    row_count: int = Field(..., ge=0)
    bytes: int = Field(..., ge=0)
    clustering_depth: float = Field(..., ge=0)
    auto_clustering: bool

class TableStorageMetric(BaseModel):
    query_id: str
    tables: List[TableStorage]

class WarehouseMetric(BaseModel):
    query_id: str
    warehouse_name: str
    credits_used: float = Field(..., ge=0)
    avg_running_queries: int = Field(..., ge=0)
    