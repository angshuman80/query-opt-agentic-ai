from fastmcp import FastMCP
from query_response import QueryHistoryRecord, QueryProfile, TableStorageMetric, WarehouseMetric
from datetime import datetime
import json

mcp = FastMCP("query-optimizer")



@mcp.tool(name="get_query_history",
 description="Get the query history for a given query id.")
def get_query_history(query_id:str)->dict:
    """Get the query history for a given query id.
    
    Args:
        query_id (str): The query id.
        
    Returns:
        QueryHistoryRecord: The query history record.
    """
    query_history = QueryHistoryRecord(
    query_id=query_id,
    query_text="SELECT * FROM fact_sales f JOIN dim_customer d ON f.cust_id = d.id",
    warehouse_name="XL_WH",
    execution_time_ms=185000,
    bytes_scanned=980000000000,
    rows_produced=120000,
    start_time=datetime.now()
)
    
    dict = { "query_id": query_id , "query_history": query_history}
    if dict["query_id"] == query_id:
        return dict["query_history"].model_dump()
    else:
        raise ToolException("Query not found")

@mcp.tool(name="get_query_profile",
description="Get the query profile for a given query id.")
def get_query_profile(query_id:str)->dict:
    """Get the query profile for a given query id.
    
    Args:
        query_id (str): The query id.
        
    Returns:
        QueryProfile: The query profile.
    """
    query_profile = QueryProfile.model_validate({
    "query_id": query_id,
    "operators": [
        {
            "operator_type": "TableScan",
            "table_name": "FACT_SALES",
            "bytes_scanned": 950000000000,
            "partition_pruning": "NONE"
        },
        {
            "operator_type": "HashJoin",
            "join_type": "INNER",
            "left_rows": 500000000,
            "right_rows": 120000
        }
    ],
    "total_elapsed_time_ms": 185000
    })

    dict = { "query_id": query_id , "query_profile": query_profile}

    if dict["query_id"] == query_id:
        return dict["query_profile"].model_dump()
    else:
        raise ToolException("Query not found")

@mcp.tool(name="get_table_storage_metric",
description="Get the table storage metric for a given query id.")
def get_table_storage_metric(query_id:str):
    """Get the table storage metric for a given query id.
    Args:
        query_id (str): The query id.
        
    Returns:
        TableStorageMetric: The table storage metric.
    """
    table_storage_metric = TableStorageMetric.model_validate(
        {
          "query_id": query_id,
          "tables": [
            {
            "table_name": "FACT_SALES",
            "row_count": 520000000,
            "bytes": 1200000000000,
            "clustering_depth": 4.9,
            "auto_clustering": False
            }
        ]
        }
     )
     
    dict = { "query_id": query_id , "table_storage_metric": table_storage_metric}
    if dict["query_id"] == query_id:
        return dict["table_storage_metric"].model_dump()
    else:
        raise ToolException("Query not found")

@mcp.tool(name="get_wareHouse_metric",
description="Get the warehouse metric for a given query id.")
def get_warehouse_metric(query_id:str,wh:str)->dict:
    """ Get the warehouse metric for a given query id. 
    Args:
        query_id (str): The query id.
        wh (str): The warehouse name.
    Returns:
        WarehouseMetric: The warehouse metric.
    """
    wh_metric = WarehouseMetric.model_validate(
        {
          "query_id": query_id,
          "warehouse_name": wh,
          "credits_used": 38.6,
          "avg_running_queries": 6
  }
    )
    dict = { "query_id": query_id , "warehouse_metric": wh_metric}
    if dict["query_id"] == query_id:
        return dict["warehouse_metric"].model_dump()
    else:
        raise ToolException("Query not found")

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
