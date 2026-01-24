"""
LangGraph workflow for query optimization.
This module defines the main workflow that orchestrates query analysis and optimization.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.model.state import QueryOptimizerState, QueryMetadata, QueryAnalysis
from src.agent.query_analyzer_agent import query_analyzer_node
from src.config import Config

# Initialize memory for conversation history
memory = MemorySaver()

def create_query_optimizer_workflow() -> StateGraph:
    """
    Create and configure the query optimizer workflow.
    
    Returns:
        Configured StateGraph workflow
    """
    
    # Create the workflow graph
    workflow = StateGraph(QueryOptimizerState)
    
    # Add nodes
    workflow.add_node("query_analyzer", query_analyzer_node)
    
    # Define the workflow edges
    workflow.set_entry_point("query_analyzer")
    workflow.add_edge("query_analyzer", END)
    
    # Compile the workflow with memory
    app = workflow.compile(checkpointer=memory)
    
    return app

async def run_query_analysis(query_metadata: QueryMetadata) -> QueryAnalysis:
    """
    Run the query analysis workflow.
    
    Args:
        query_metadata: Query metadata to analyze
        
    Returns:
        QueryAnalysis results
    """
    
    # Create the workflow
    app = create_query_optimizer_workflow()
    
    # Initialize state
    initial_state = QueryOptimizerState(
        query=query_metadata,
        query_analysis=QueryAnalysis(
            query_id="",
            query_text="",
            severity="",
            issues=[],
            root_cause="",
            cost_drivers={}
        )
    )
    
    # Run the workflow
    config = {"configurable": {"thread_id": f"query_{query_metadata.query_id}"}}
    
    try:
        result = await app.ainvoke(initial_state, config=config)
        return result["query_analysis"]
        
    except Exception as e:
        print(f"Workflow execution failed: {str(e)}")
        
        # Return error analysis
        return QueryAnalysis(
            query_id=query_metadata.query_id,
            query_text="",
            severity="error",
            issues=[f"Workflow failed: {str(e)}"],
            root_cause="System error",
            cost_drivers={}
        )

# Example usage and testing functions
def create_sample_query_metadata() -> QueryMetadata:
    """Create sample query metadata for testing."""
    return QueryMetadata(
        user_name="test_user",
        query_id="test_query_123",
        workspace_name="test_workspace",
        workspace_id="ws_123",
        tenant_id="tenant_456",
        warehouse_type="XL",
        date_time=datetime.now()
    )

async def main():
    """Main function to test the workflow."""
    print("Starting Query Optimizer Workflow Test")
    
    # Create sample query metadata
    query_metadata = create_sample_query_metadata()
    
    print(f"Analyzing query: {query_metadata.query_id}")
    
    # Run the analysis
    analysis = await run_query_analysis(query_metadata)

    print(f"""Type of analysis: {type(analysis)}""")
    
    # Print results
    print("\n=== Query Analysis Results ===")
    print(f"Query ID: {analysis.query_id}")
    print(f"Severity: {analysis.severity}")
    print(f"Issues: {analysis.issues}")
    print(f"Root Cause: {analysis.root_cause}")
    print(f"Cost Drivers: {analysis.cost_drivers}")



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())