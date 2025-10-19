#!/usr/bin/env python3
"""
HTTP Bridge for MCP Server - Ecological Predictor
Exposes MCP server tools as HTTP endpoints for ElevenLabs AI Agent integration
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import for serving graphs
OUTPUT_DIR = "simulation_outputs"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MCP client session
mcp_session = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup MCP client"""
    global mcp_session
    
    # Startup: Initialize MCP client
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=None
    )
    
    try:
        # Create stdio connection to MCP server (use async context manager)
        async with stdio_client(server_params) as (mcp_read, mcp_write):
            # Initialize session (also use async context manager)
            async with ClientSession(mcp_read, mcp_write) as session:
                mcp_session = session
                await mcp_session.initialize()
                
                logger.info("✓ MCP client initialized successfully")
                
                yield
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize MCP client: {e}")
        raise

# Create FastAPI app with lifespan
app = FastAPI(
    title="AURA Ecology MCP Bridge",
    description="HTTP bridge for AURA Ecology MCP Server",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for ElevenLabs integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to bypass ngrok browser warning
@app.middleware("http")
async def add_ngrok_skip_header(request: Request, call_next):
    """Add header to bypass ngrok browser warning on free tier"""
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response


# Request models for validation
class ReportRequest(BaseModel):
    analysis_focus: Optional[str] = "overall"

class SimulationRequest(BaseModel):
    initial_prey: Optional[float] = 40
    initial_predators: Optional[float] = 5
    years: Optional[float] = 50
    prey_growth_rate: Optional[float] = 0.5
    predation_rate: Optional[float] = 0.02
    predator_efficiency: Optional[float] = 0.01
    predator_death_rate: Optional[float] = 0.3

class RiskRequest(BaseModel):
    species: Optional[str] = "predator"
    years_to_analyze: Optional[float] = 10


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AURA Ecology MCP Bridge",
        "version": "1.0.0",
        "description": "HTTP Bridge for AURA Ecological MCP Server",
        "status": "operational",
        "mcp_connected": mcp_session is not None,
        "protocol": "mcp",
        "endpoints": {
            "GET /health": "Health check",
            "GET /tools": "List available MCP tools",
            "GET /mcp/list-tools": "MCP protocol tool listing",
            "POST /tools/generate_ecological_report": "Generate analysis report",
            "POST /tools/calculate_extinction_risk": "Calculate extinction risk",
            "POST /tools/run_lotka_volterra_simulation": "Run prediction simulation",
            "GET /sse": "Server-Sent Events for streaming",
            "POST /mcp": "Generic MCP tool call",
            "GET /graphs/{filename}": "Retrieve generated graphs"
        }
    }


# MCP Protocol Endpoints for ElevenLabs
@app.get("/mcp/list-tools")
@app.post("/mcp/list-tools")
async def mcp_list_tools():
    """MCP protocol endpoint for listing tools - compatible with ElevenLabs"""
    if not mcp_session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")
    
    try:
        tools = await mcp_session.list_tools()
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools.tools
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error listing tools via MCP protocol: {e}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "MCP HTTP Bridge is running",
        "mcp_connected": mcp_session is not None
    }


@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    if not mcp_session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")
    
    try:
        tools = await mcp_session.list_tools()
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools.tools
            ]
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/generate_ecological_report")
async def generate_ecological_report_endpoint(request: ReportRequest = None):
    """
    Generate comprehensive ecological analysis report.
    
    Analyzes historical population data from simulation runs.
    Returns statistics, trends, and ecological insights using APES terminology.
    """
    if not mcp_session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")
    
    try:
        arguments = request.dict() if request else {}
        result = await mcp_session.call_tool("generate_ecological_report", arguments=arguments)
        
        # Extract text content from result
        if hasattr(result, 'content') and result.content:
            content = result.content[0]
            if hasattr(content, 'text'):
                return JSONResponse(content={
                    "status": "success",
                    "tool": "generate_ecological_report",
                    "result": content.text
                })
        
        return JSONResponse(content={
            "status": "success",
            "tool": "generate_ecological_report",
            "result": str(result)
        })
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/run_lotka_volterra_simulation")
async def run_lotka_volterra_simulation_endpoint(request: SimulationRequest):
    """
    Run Lotka-Volterra predictive simulation.
    
    Generates population forecasts and visualizations for what-if scenarios.
    Returns predictions and URL to generated graph.
    """
    if not mcp_session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")
    
    try:
        result = await mcp_session.call_tool("run_lotka_volterra_simulation", arguments=request.dict())
        
        # Extract text content
        if hasattr(result, 'content') and result.content:
            content = result.content[0]
            if hasattr(content, 'text'):
                return JSONResponse(content={
                    "status": "success",
                    "tool": "run_lotka_volterra_simulation",
                    "result": content.text
                })
        
        return JSONResponse(content={
            "status": "success",
            "tool": "run_lotka_volterra_simulation",
            "result": str(result)
        })
        
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/calculate_extinction_risk")
async def calculate_extinction_risk_endpoint(request: RiskRequest = None):
    """
    Calculate extinction risk assessment.
    
    Analyzes recent population trends to determine extinction probability.
    Returns risk score (1-10) and vulnerability factors.
    """
    if not mcp_session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")
    
    try:
        arguments = request.dict() if request else {}
        result = await mcp_session.call_tool("calculate_extinction_risk", arguments=arguments)
        
        # Extract text content
        if hasattr(result, 'content') and result.content:
            content = result.content[0]
            if hasattr(content, 'text'):
                return JSONResponse(content={
                    "status": "success",
                    "tool": "calculate_extinction_risk",
                    "result": content.text
                })
        
        return JSONResponse(content={
            "status": "success",
            "tool": "calculate_extinction_risk",
            "result": str(result)
        })
        
    except Exception as e:
        logger.error(f"Error calculating extinction risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/graphs/{filename}")
async def get_graph(filename: str):
    """
    Serve generated prediction graphs.
    
    Returns PNG images generated by the Lotka-Volterra simulation tool.
    """
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Graph not found")
    return FileResponse(file_path, media_type="image/png")


@app.get("/graphs")
async def list_graphs():
    """List all available prediction graphs."""
    try:
        graphs = []
        if os.path.exists(OUTPUT_DIR):
            for filename in os.listdir(OUTPUT_DIR):
                if filename.endswith('.png'):
                    graphs.append({
                        "filename": filename,
                        "url": f"/graphs/{filename}",
                        "path": os.path.join(OUTPUT_DIR, filename)
                    })
        return {"graphs": graphs, "count": len(graphs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sse")
@app.post("/sse")
async def sse_endpoint(request: Request = None):
    """
    Server-Sent Events endpoint for streaming MCP responses.
    This is used by ElevenLabs to discover and connect to MCP tools.
    Supports both GET and POST methods for compatibility.
    """
    if not mcp_session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")
    
    async def event_generator():
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'message': 'MCP Bridge connected'})}\n\n"
            
            # List available tools
            tools = await mcp_session.list_tools()
            tools_data = {
                "type": "tools",
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools.tools
                ]
            }
            yield f"data: {json.dumps(tools_data)}\n\n"
            
            # Keep connection alive with pings
            while True:
                await asyncio.sleep(30)
                yield f"data: {json.dumps({'type': 'ping', 'timestamp': asyncio.get_event_loop().time()})}\n\n"
                
        except asyncio.CancelledError:
            logger.info("SSE connection closed")
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )


@app.post("/mcp")
async def mcp_call(request: Request):
    """
    Generic MCP tool call endpoint.
    Allows calling any MCP tool by name with custom arguments.
    """
    if not mcp_session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")
    
    try:
        body = await request.json()
        tool_name = body.get("tool")
        arguments = body.get("arguments", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing 'tool' parameter")
        
        result = await mcp_session.call_tool(tool_name, arguments=arguments)
        
        # Extract text content
        if hasattr(result, 'content') and result.content:
            content = result.content[0]
            if hasattr(content, 'text'):
                return JSONResponse(content={
                    "status": "success",
                    "tool": tool_name,
                    "result": content.text
                })
        
        return JSONResponse(content={
            "status": "success",
            "tool": tool_name,
            "result": str(result)
        })
        
    except Exception as e:
        logger.error(f"Error calling tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    print("=" * 70)
    print("AURA ECOLOGY MCP HTTP BRIDGE")
    print("=" * 70)
    print("\n🚀 Starting server on http://localhost:8080")
    print("\n📡 Available endpoints:")
    print("  GET  /health                                  - Health check")
    print("  GET  /tools                                   - List available MCP tools")
    print("  POST /tools/generate_ecological_report       - Generate analysis report")
    print("  POST /tools/calculate_extinction_risk        - Calculate extinction risk")
    print("  POST /tools/run_lotka_volterra_simulation    - Run prediction simulation")
    print("  GET  /sse                                     - Server-Sent Events")
    print("  POST /mcp                                     - Generic MCP tool call")
    print("  GET  /graphs/{filename}                       - Serve generated graphs")
    print("\n🌐 For ElevenLabs integration:")
    print("  Configure with: https://YOUR-NGROK-URL.ngrok-free.app/sse")
    print("\n⏹️  Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
