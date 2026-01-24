from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain.agents import create_agent
from langchain_classic.agents import AgentExecutor
from src.model.state import QueryMetadata, QueryAnalysis, QueryOptimizerState
from src.model.prompt import ANALYZER_REACT_PROMPT
from langchain_groq import ChatGroq
from typing import Dict, Any
import json

async def query_analyzer_agent(query_metadata: QueryMetadata):
    """
    Analyze the query and extract relevant information.
    
    Args:
        query_metadata: Query metadata containing user_name, query_id, workspace_name, workspace_id, tenant_id, warehouse_type, date_time
        
    Returns:
        QueryAnalysis object with extracted information
    """
    client = MultiServerMCPClient(  
    {
        "query-optimizer": {
            "transport": "http",  # HTTP-based remote server
            # Ensure you start your weather server on port 8000
            "url": "http://localhost:8000/mcp",
        }
    }
   )

    tools = await client.get_tools() 
    print(f"Tools from MCP server: {tools}")
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    
    # Create agent with tools
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt= ANALYZER_REACT_PROMPT,
        debug=True
        )
    
    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": f"Analyze this query: {query_metadata.query_id}"}
        ]
    })
    
    print(f"response of the llm call {response}")
    
    # Convert agent response to expected format
    if isinstance(response, dict) and "messages" in response:
        # Extract the content from the last message
        messages = response.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                content = last_message.content
            else:
                content = str(last_message)
        else:
            content = str(response)
    else:
        content = str(response)
    
    # Return in the expected format for LangGraph
    return {
        "output": content,
        "intermediate_steps": []
    }

async def query_analyzer_node(state: QueryOptimizerState) -> Dict[str, Any]:
    """
    LangGraph node for query analysis.
    
    Args:
        state: Current workflow state containing query metadata
        
    Returns:
        Updated state with query analysis results
    """
    print(f"Starting query analysis for query_id: {state.query.query_id}")
    
    try:
        # Run the query analyzer agent
        result = await query_analyzer_agent(state.query)
        
        # Parse the JSON output from the agent
        try:
            analysis_data = json.loads(result["output"])
            
            # Create QueryAnalysis object
            query_analysis = QueryAnalysis(
                query_id=analysis_data.get("query_id", state.query.query_id),
                query_text="",  # This would be populated from MCP tools
                severity=analysis_data.get("severity", "unknown"),
                issues=analysis_data.get("issues", []),
                root_cause=analysis_data.get("root_cause", ""),
                cost_drivers=analysis_data.get("cost_drivers", {})
            )
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            query_analysis = QueryAnalysis(
                query_id=state.query.query_id,
                query_text="",
                severity="error",
                issues=["Failed to parse agent output"],
                root_cause="JSON parsing error",
                cost_drivers={}
            )
        
        print(f"Query analysis completed for query_id: {state.query.query_id}")
        
        return {
            "query_analysis": query_analysis
        }
        
    except Exception as e:
        print(f"Error in query analysis: {str(e)}")
        
        # Return error state
        error_analysis = QueryAnalysis(
            query_id=state.query.query_id,
            query_text="",
            severity="error",
            issues=[f"Analysis failed: {str(e)}"],
            root_cause="Agent execution error",
            cost_drivers={}
        )
        
        return {
            "query_analysis": error_analysis
        }