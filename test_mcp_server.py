#!/usr/bin/env python3
"""
Test script for MCP Server - Ecological Predictor
Tests all three tools to ensure they work correctly
"""

import asyncio
import sys
from mcp_server import (
    generate_ecological_report,
    run_lotka_volterra_simulation,
    calculate_extinction_risk,
    load_population_data
)


async def test_all_tools():
    """Test all three MCP tools."""
    print("=" * 70)
    print("TESTING MCP SERVER - ECOLOGICAL PREDICTOR")
    print("=" * 70)
    
    # Check if data exists
    data = load_population_data()
    if not data:
        print("\n⚠️  WARNING: No simulation data found in data.csv")
        print("   Please run 'python main.py' first to generate data.")
        print("\n   For testing purposes, we'll continue with predictions...")
    else:
        print(f"\n✓ Found {len(data)} data points in simulation data")
    
    print("\n" + "-" * 70)
    print("TEST 1: generate_ecological_report")
    print("-" * 70)
    
    try:
        result = await generate_ecological_report({"analysis_focus": "overall"})
        print(result[0].text)
        print("\n✓ Test 1 PASSED")
    except Exception as e:
        print(f"\n✗ Test 1 FAILED: {e}")
        return False
    
    print("\n" + "-" * 70)
    print("TEST 2: run_lotka_volterra_simulation")
    print("-" * 70)
    
    try:
        result = await run_lotka_volterra_simulation({
            "initial_prey": 40,
            "initial_predators": 5,
            "years": 30,
            "prey_growth_rate": 0.5,
            "predation_rate": 0.02,
            "predator_efficiency": 0.01,
            "predator_death_rate": 0.3
        })
        print(result[0].text)
        print("\n✓ Test 2 PASSED")
    except Exception as e:
        print(f"\n✗ Test 2 FAILED: {e}")
        return False
    
    print("\n" + "-" * 70)
    print("TEST 3: calculate_extinction_risk")
    print("-" * 70)
    
    try:
        result = await calculate_extinction_risk({
            "species": "both",
            "years_to_analyze": 10
        })
        print(result[0].text)
        print("\n✓ Test 3 PASSED")
    except Exception as e:
        print(f"\n✗ Test 3 FAILED: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)
    print("\nMCP Server is ready to use!")
    print("\nNext steps:")
    print("  1. For Claude Desktop: Add server to claude_desktop_config.json")
    print("  2. For ElevenLabs: Run 'python mcp_http_bridge.py'")
    print("  3. For direct Python: Import functions from mcp_server.py")
    print("\nSee MCP_SETUP_GUIDE.md for detailed instructions.")
    
    return True


async def quick_test():
    """Quick test to verify imports work."""
    print("Testing MCP server imports...")
    try:
        from mcp_server import SERVER_NAME
        print(f"✓ MCP Server: {SERVER_NAME}")
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements_mcp.txt")
        return False


if __name__ == "__main__":
    print("\nChecking dependencies...")
    
    # Quick import test
    if not asyncio.run(quick_test()):
        sys.exit(1)
    
    print("\nRunning full test suite...\n")
    
    # Run full tests
    success = asyncio.run(test_all_tools())
    
    if not success:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)
    else:
        sys.exit(0)
