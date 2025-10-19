# Quick Start Script for MCP Server
# Run this in PowerShell

Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host "ECOLOGICAL PREDICTOR MCP SERVER - QUICK START"
Write-Host "=" -NoNewline; Write-Host ("=" * 69)

# Step 1: Check Python
Write-Host "`nStep 1: Checking Python installation..."
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Step 2: Activate virtual environment (if exists)
if (Test-Path "env\Scripts\Activate.ps1") {
    Write-Host "`nStep 2: Activating virtual environment..."
    & .\env\Scripts\Activate.ps1
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "`nStep 2: No virtual environment found (optional)" -ForegroundColor Yellow
}

# Step 3: Install dependencies
Write-Host "`nStep 3: Installing MCP server dependencies..."
Write-Host "Running: pip install -r requirements_mcp.txt"
pip install -r requirements_mcp.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 4: Run test
Write-Host "`nStep 4: Testing MCP server..."
python test_mcp_server.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ MCP Server is working correctly!" -ForegroundColor Green
} else {
    Write-Host "`n✗ MCP Server test failed" -ForegroundColor Red
    exit 1
}

# Step 5: Instructions
Write-Host "`n" -NoNewline; Write-Host ("=" * 70)
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host ("=" * 70)
Write-Host "`nYour MCP server is ready. Choose an integration option:"
Write-Host "`n1. CLAUDE DESKTOP:" -ForegroundColor Cyan
Write-Host "   - Edit: %APPDATA%\Claude\claude_desktop_config.json"
Write-Host "   - Add the configuration from mcp_config.json"
Write-Host "   - Restart Claude Desktop"

Write-Host "`n2. ELEVENLABS AI AGENT:" -ForegroundColor Cyan
Write-Host "   - Run: python mcp_http_bridge.py"
Write-Host "   - Configure agent at: https://elevenlabs.io/app/talk-to?agent_id=agent_0101k7vyy29heqr9rvy4fmqs6psv"
Write-Host "   - Add HTTP endpoints from http://127.0.0.1:8080"

Write-Host "`n3. DIRECT PYTHON:" -ForegroundColor Cyan
Write-Host "   - Import: from mcp_server import *"
Write-Host "   - Call functions directly in your code"

Write-Host "`nFor detailed instructions, see: MCP_SETUP_GUIDE.md"
Write-Host ("=" * 70)
