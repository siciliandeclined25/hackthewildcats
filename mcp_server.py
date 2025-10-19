#!/usr/bin/env python3
"""
MCP Server: Ecological Predictor
An MCP server for ecological simulation analysis, prediction, and risk assessment.
"""

import json
import os
import csv
import math
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple
import asyncio

# MCP SDK imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("Error: MCP SDK not installed. Please run: pip install mcp")
    exit(1)

# Configuration
DATA_FILE = "population_data.csv"
CONTEXT_FILE = "TOTC_CONTEXT.json"
OUTPUT_DIR = "simulation_outputs"
SERVER_NAME = "Ecological Predictor"

# Ensure output directory exists
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Create the MCP server instance
server = Server(SERVER_NAME)


def load_population_data() -> List[Dict[str, float]]:
    """Load population data from CSV file."""
    data = []
    try:
        with open(DATA_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    'time': float(row['time']),
                    'prey': int(row['prey']),
                    'predators': int(row['predators'])
                })
    except FileNotFoundError:
        return []
    return data


def calculate_statistics(data: List[Dict[str, float]]) -> Dict[str, Any]:
    """Calculate statistical measures from population data."""
    if not data:
        return {}
    
    prey_populations = [d['prey'] for d in data]
    predator_populations = [d['predators'] for d in data]
    
    stats = {
        'prey_avg': np.mean(prey_populations),
        'prey_max': max(prey_populations),
        'prey_min': min(prey_populations),
        'prey_std': np.std(prey_populations),
        'predator_avg': np.mean(predator_populations),
        'predator_max': max(predator_populations),
        'predator_min': min(predator_populations),
        'predator_std': np.std(predator_populations),
        'total_years': data[-1]['time'] if data else 0
    }
    
    # Find extinction events
    prey_extinct_time = next((d['time'] for d in data if d['prey'] == 0), None)
    predator_extinct_time = next((d['time'] for d in data if d['predators'] == 0), None)
    
    stats['prey_extinction_time'] = prey_extinct_time
    stats['predator_extinction_time'] = predator_extinct_time
    
    return stats


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources (context file)."""
    return [
        types.Resource(
            uri=f"file:///{CONTEXT_FILE}",
            name="Ecological Simulation Context",
            description="Contains simulation rules, species information, and historical data",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read the context resource."""
    if CONTEXT_FILE in uri:
        # Load current data and create context
        data = load_population_data()
        stats = calculate_statistics(data)
        
        context = {
            "simulation_name": "AURA Ecology Simulation",
            "description": "A predator-prey ecological simulation based on r/K selection theory",
            "species": {
                "prey": {
                    "name": "Rabbit",
                    "type": "r-selected",
                    "characteristics": "High reproduction rate, short lifespan, rapid population growth",
                    "strategy": "Opportunistic, fast-breeding species that thrives when resources are abundant"
                },
                "predator": {
                    "name": "Bobcat/Coyote",
                    "type": "K-selected",
                    "characteristics": "Low reproduction rate, longer lifespan, stable population",
                    "strategy": "Equilibrium species that maintains stable population near carrying capacity"
                }
            },
            "simulation_rules": {
                "prey_growth": "Exponential growth when predators are absent",
                "predation": "Predators consume prey at a rate proportional to encounters",
                "predator_decline": "Predators die off when prey becomes scarce",
                "carrying_capacity": "Environment can support limited populations"
            },
            "current_statistics": stats,
            "last_updated": datetime.now().isoformat()
        }
        
        return json.dumps(context, indent=2)
    
    raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="generate_ecological_report",
            description="Analyzes historical population data from the simulation and generates a comprehensive ecological report. Use this to answer questions about past simulation runs, population trends, average growth rates, extinction events, and overall ecosystem dynamics. Returns a detailed analysis using APES (AP Environmental Science) terminology.",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_focus": {
                        "type": "string",
                        "description": "Optional focus area: 'overall', 'prey', 'predator', or 'interactions'",
                        "default": "overall"
                    }
                }
            }
        ),
        types.Tool(
            name="run_lotka_volterra_simulation",
            description="Runs a predictive Lotka-Volterra mathematical model to forecast population dynamics. Use this for 'what-if' scenarios, predictions, and theoretical modeling. Generates a visualization graph showing population trends over time. Specify initial populations and simulation parameters to see how the ecosystem would evolve.",
            inputSchema={
                "type": "object",
                "properties": {
                    "initial_prey": {
                        "type": "number",
                        "description": "Starting prey (rabbit) population",
                        "default": 40
                    },
                    "initial_predators": {
                        "type": "number",
                        "description": "Starting predator (coyote/bobcat) population",
                        "default": 5
                    },
                    "years": {
                        "type": "number",
                        "description": "Number of years to simulate",
                        "default": 50
                    },
                    "prey_growth_rate": {
                        "type": "number",
                        "description": "Prey natural growth rate (alpha)",
                        "default": 0.5
                    },
                    "predation_rate": {
                        "type": "number",
                        "description": "Predation efficiency (beta)",
                        "default": 0.02
                    },
                    "predator_efficiency": {
                        "type": "number",
                        "description": "Predator reproduction efficiency (delta)",
                        "default": 0.01
                    },
                    "predator_death_rate": {
                        "type": "number",
                        "description": "Predator natural death rate (gamma)",
                        "default": 0.3
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="calculate_extinction_risk",
            description="Calculates the short-term extinction probability for predator or prey populations based on recent population data trends. Analyzes volatility, minimum population thresholds, and food source stability. Use this to assess ecosystem health and identify vulnerable species. Returns an extinction risk score (1-10) with detailed vulnerability factors.",
            inputSchema={
                "type": "object",
                "properties": {
                    "species": {
                        "type": "string",
                        "description": "Species to analyze: 'prey', 'predator', or 'both'",
                        "default": "predator"
                    },
                    "years_to_analyze": {
                        "type": "number",
                        "description": "Number of recent years to analyze (default: 10)",
                        "default": 10
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution."""
    
    if name == "generate_ecological_report":
        return await generate_ecological_report(arguments or {})
    elif name == "run_lotka_volterra_simulation":
        return await run_lotka_volterra_simulation(arguments or {})
    elif name == "calculate_extinction_risk":
        return await calculate_extinction_risk(arguments or {})
    else:
        raise ValueError(f"Unknown tool: {name}")


async def generate_ecological_report(args: Dict[str, Any]) -> list[types.TextContent]:
    """Generate comprehensive ecological analysis report."""
    focus = args.get('analysis_focus', 'overall')
    
    data = load_population_data()
    if not data:
        return [types.TextContent(
            type="text",
            text="No historical data available. Please run the simulation first to collect population data."
        )]
    
    stats = calculate_statistics(data)
    
    # Generate report based on focus
    report_lines = [
        "=" * 60,
        "ECOLOGICAL SIMULATION REPORT",
        "=" * 60,
        f"\nAnalysis Focus: {focus.upper()}",
        f"Data Period: Years 0 to {stats['total_years']:.0f}",
        f"Total Data Points: {len(data)}",
        "\n" + "-" * 60
    ]
    
    if focus in ['overall', 'prey']:
        report_lines.extend([
            "\nPREY POPULATION ANALYSIS (r-selected species - Rabbits)",
            "-" * 60,
            f"Average Population: {stats['prey_avg']:.1f} individuals",
            f"Maximum Population: {stats['prey_max']} individuals (Peak Overshoot)",
            f"Minimum Population: {stats['prey_min']} individuals",
            f"Population Volatility (Std Dev): {stats['prey_std']:.2f}",
        ])
        
        if stats['prey_extinction_time']:
            report_lines.append(f"⚠️  EXTINCTION EVENT at Year {stats['prey_extinction_time']}")
        else:
            report_lines.append("✓ Species remained viable throughout simulation")
        
        # r-selection characteristics
        if stats['prey_std'] > stats['prey_avg'] * 0.3:
            report_lines.append("\n📊 r-Selection Pattern: HIGH population volatility observed")
            report_lines.append("   Characteristic of opportunistic species with boom-bust cycles")
    
    if focus in ['overall', 'predator']:
        report_lines.extend([
            "\n\nPREDATOR POPULATION ANALYSIS (K-selected species - Bobcats/Coyotes)",
            "-" * 60,
            f"Average Population: {stats['predator_avg']:.1f} individuals",
            f"Maximum Population: {stats['predator_max']} individuals",
            f"Minimum Population: {stats['predator_min']} individuals",
            f"Population Stability (Std Dev): {stats['predator_std']:.2f}",
        ])
        
        if stats['predator_extinction_time']:
            report_lines.append(f"⚠️  EXTINCTION EVENT at Year {stats['predator_extinction_time']}")
        else:
            report_lines.append("✓ Species maintained throughout simulation")
        
        # K-selection characteristics
        if stats['predator_std'] < stats['predator_avg'] * 0.3:
            report_lines.append("\n📊 K-Selection Pattern: LOW population volatility observed")
            report_lines.append("   Characteristic of equilibrium species near carrying capacity")
    
    if focus in ['overall', 'interactions']:
        report_lines.extend([
            "\n\nPREDATOR-PREY DYNAMICS",
            "-" * 60,
            f"Prey-to-Predator Ratio: {stats['prey_avg']/max(stats['predator_avg'], 1):.1f}:1",
        ])
        

        if stats['prey_std'] > stats['prey_avg'] * 0.5:
            report_lines.append("⚠️  HIGH INSTABILITY: Extreme population fluctuations detected")
            report_lines.append("   Indicates oscillatory dynamics characteristic of Lotka-Volterra systems")
        else:
            report_lines.append("✓ STABLE SYSTEM: Populations show moderate variation")
            report_lines.append("   System approaching equilibrium state")
    
    report_lines.extend([
        "\n" + "=" * 60,
        "END OF REPORT",
        "=" * 60
    ])
    
    return [types.TextContent(type="text", text="\n".join(report_lines))]


async def run_lotka_volterra_simulation(args: Dict[str, Any]) -> list[types.TextContent]:
    """Run Lotka-Volterra predictive simulation."""

    prey_0 = args.get('initial_prey', 40)
    pred_0 = args.get('initial_predators', 5)
    years = args.get('years', 50)
    alpha = args.get('prey_growth_rate', 0.5)  # prey growth rate
    beta = args.get('predation_rate', 0.02)    # predation rate
    delta = args.get('predator_efficiency', 0.01)  # predator efficiency
    gamma = args.get('predator_death_rate', 0.3)   # predator death rate
    
    # Time steps
    dt = 0.1
    steps = int(years / dt)
    
    # Arrays to store results
    time = np.zeros(steps)
    prey = np.zeros(steps)
    predators = np.zeros(steps)
    
    # Initial conditions
    prey[0] = prey_0
    predators[0] = pred_0
    
    # Lotka-Volterra equations (discrete time)
    for i in range(1, steps):
        time[i] = i * dt
        
        # dPrey/dt = alpha*Prey - beta*Prey*Predators
        # dPredators/dt = delta*Prey*Predators - gamma*Predators
        
        prey_change = (alpha * prey[i-1] - beta * prey[i-1] * predators[i-1]) * dt
        pred_change = (delta * prey[i-1] * predators[i-1] - gamma * predators[i-1]) * dt
        
        prey[i] = max(0, prey[i-1] + prey_change)
        predators[i] = max(0, predators[i-1] + pred_change)
        
        # Check for extinction
        if prey[i] < 0.1:
            prey[i] = 0
        if predators[i] < 0.1:
            predators[i] = 0
    
    # Generate plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lotka_volterra_prediction_{timestamp}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    plt.figure(figsize=(12, 6))
    plt.plot(time, prey, 'b-', label='Prey (Rabbits)', linewidth=2)
    plt.plot(time, predators, 'r-', label='Predators (Bobcats)', linewidth=2)
    plt.xlabel('Time (years)', fontsize=12)
    plt.ylabel('Population', fontsize=12)
    plt.title('Lotka-Volterra Population Dynamics Prediction', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close()
    
    # Analyze results
    prey_extinct = np.min(prey) < 1
    pred_extinct = np.min(predators) < 1
    
    final_prey = prey[-1]
    final_pred = predators[-1]
    
    # Generate narrative
    narrative = [
        "=" * 60,
        "LOTKA-VOLTERRA PREDICTIVE SIMULATION",
        "=" * 60,
        f"\nInitial Conditions:",
        f"  • Prey Population: {prey_0}",
        f"  • Predator Population: {pred_0}",
        f"\nModel Parameters:",
        f"  • Prey Growth Rate (α): {alpha}",
        f"  • Predation Rate (β): {beta}",
        f"  • Predator Efficiency (δ): {delta}",
        f"  • Predator Death Rate (γ): {gamma}",
        f"\nSimulation Duration: {years} years",
        "\n" + "-" * 60,
        "\nFORECAST RESULTS:",
        "-" * 60,
    ]
    
    if prey_extinct:
        extinction_time = time[np.where(prey < 1)[0][0]]
        narrative.append(f"⚠️  PREY EXTINCTION predicted at Year {extinction_time:.1f}")
        narrative.append("   Without prey, predator population will also collapse")
    elif pred_extinct:
        extinction_time = time[np.where(predators < 1)[0][0]]
        narrative.append(f"⚠️  PREDATOR EXTINCTION predicted at Year {extinction_time:.1f}")
        narrative.append("   Prey population will grow exponentially without predation")
    else:
        narrative.extend([
            f"Final Prey Population: {final_prey:.0f} individuals",
            f"Final Predator Population: {final_pred:.0f} individuals",
        ])
        
        # Check for oscillations
        prey_range = np.max(prey) - np.min(prey)
        if prey_range > prey_0:
            narrative.append("\n📊 OSCILLATORY DYNAMICS detected")
            narrative.append("   Populations exhibit cyclic boom-bust patterns")
            narrative.append("   This is characteristic of classic predator-prey relationships")
        else:
            narrative.append("\n✓ STABLE EQUILIBRIUM trend")
            narrative.append("   Populations converging toward balance")
    
    narrative.extend([
        f"\n📈 Visualization saved: {filename}",
        f"   Full path: {os.path.abspath(filepath)}",
        f"   🔗 View graph online: https://unequilaterally-tendrillar-kyra.ngrok-free.dev/graphs/{filename}",
        "\n" + "=" * 60
    ])
    
    return [types.TextContent(type="text", text="\n".join(narrative))]


async def calculate_extinction_risk(args: Dict[str, Any]) -> list[types.TextContent]:
    """Calculate extinction risk based on recent population trends."""
    species = args.get('species', 'predator')
    years_to_analyze = args.get('years_to_analyze', 10)
    
    data = load_population_data()
    if not data:
        return [types.TextContent(
            type="text",
            text="No historical data available for risk assessment."
        )]
    
    # Get recent data
    recent_data = data[-int(years_to_analyze):] if len(data) > years_to_analyze else data
    
    if len(recent_data) < 3:
        return [types.TextContent(
            type="text",
            text="Insufficient data for extinction risk analysis. Need at least 3 data points."
        )]
    
    report_lines = [
        "=" * 60,
        "EXTINCTION RISK ASSESSMENT",
        "=" * 60,
        f"\nAnalysis Period: Last {len(recent_data)} years",
        f"Species Under Assessment: {species.upper()}",
        "\n" + "-" * 60
    ]
    
    def assess_species_risk(pop_key: str, species_name: str, is_predator: bool = False) -> Tuple[float, str, List[str]]:
        """Assess risk for a single species."""
        populations = [d[pop_key] for d in recent_data]
        
        avg_pop = np.mean(populations)
        std_pop = np.std(populations)
        min_pop = min(populations)
        max_pop = max(populations)
        
        # Calculate coefficient of variation (CV)
        cv = (std_pop / avg_pop * 100) if avg_pop > 0 else 0
        
        risk_factors = []
        risk_score = 0.0
        
        # Factor 1: Minimum population threshold
        if min_pop == 0:
            risk_score += 3.0
            risk_factors.append("CRITICAL: Zero population events detected")
        elif min_pop < 3:
            risk_score += 2.5
            risk_factors.append("SEVERE: Population dropped below viable threshold (<3)")
        elif min_pop < 5:
            risk_score += 2.0
            risk_factors.append("HIGH: Population approached minimum viable size")
        elif min_pop < 10:
            risk_score += 1.0
            risk_factors.append("MODERATE: Low population valleys observed")
        
        # Factor 2: Population volatility
        if cv > 80:
            risk_score += 3.0
            risk_factors.append(f"CRITICAL: Extreme volatility (CV={cv:.1f}%)")
        elif cv > 50:
            risk_score += 2.0
            risk_factors.append(f"HIGH: High population instability (CV={cv:.1f}%)")
        elif cv > 30:
            risk_score += 1.0
            risk_factors.append(f"MODERATE: Notable fluctuations (CV={cv:.1f}%)")
        else:
            risk_factors.append(f"STABLE: Low volatility (CV={cv:.1f}%)")
        
        # Factor 3: Declining trend
        if len(populations) >= 3:
            recent_trend = populations[-1] - populations[-3]
            if recent_trend < -avg_pop * 0.3:
                risk_score += 2.0
                risk_factors.append("HIGH: Significant declining trend detected")
            elif recent_trend < 0:
                risk_score += 0.5
                risk_factors.append("CAUTION: Slight population decline observed")
        
        # Factor 4: For predators, check food source stability
        if is_predator:
            prey_populations = [d['prey'] for d in recent_data]
            prey_cv = (np.std(prey_populations) / np.mean(prey_populations) * 100) if np.mean(prey_populations) > 0 else 0
            
            if prey_cv > 50:
                risk_score += 1.5
                risk_factors.append(f"K-SELECTION VULNERABILITY: Food source highly volatile ({prey_cv:.1f}%)")
            elif prey_cv > 30:
                risk_score += 0.5
                risk_factors.append(f"FOOD INSTABILITY: Prey population variation at {prey_cv:.1f}%")
        
        # Determine vulnerability classification
        if risk_score >= 7:
            vulnerability = "CRITICAL - Immediate Extinction Risk"
        elif risk_score >= 5:
            vulnerability = "HIGH - Species Under Severe Threat"
        elif risk_score >= 3:
            vulnerability = "MODERATE - Vulnerable Population"
        elif risk_score >= 1:
            vulnerability = "LOW - Some Risk Factors Present"
        else:
            vulnerability = "MINIMAL - Population Stable"
        
        return min(risk_score, 10.0), vulnerability, risk_factors
    
    # Assess requested species
    if species in ['prey', 'both']:
        prey_score, prey_vuln, prey_factors = assess_species_risk('prey', 'Prey (Rabbits)', False)
        
        report_lines.extend([
            "\n🐰 PREY SPECIES (Rabbits - r-selected)",
            "-" * 60,
            f"Extinction Risk Score: {prey_score:.1f}/10.0",
            f"Vulnerability Classification: {prey_vuln}",
            "\nRisk Factors Identified:"
        ])
        for factor in prey_factors:
            report_lines.append(f"  • {factor}")
    
    if species in ['predator', 'both']:
        pred_score, pred_vuln, pred_factors = assess_species_risk('predators', 'Predators', True)
        
        report_lines.extend([
            "\n🐱 PREDATOR SPECIES (Bobcats/Coyotes - K-selected)",
            "-" * 60,
            f"Extinction Risk Score: {pred_score:.1f}/10.0",
            f"Vulnerability Classification: {pred_vuln}",
            "\nRisk Factors Identified:"
        ])
        for factor in pred_factors:
            report_lines.append(f"  • {factor}")
    
    # Recommendations
    report_lines.extend([
        "\n" + "-" * 60,
        "CONSERVATION RECOMMENDATIONS:",
        "-" * 60
    ])
    
    if species in ['predator', 'both']:
        if pred_score >= 7:
            report_lines.append("⚠️  URGENT ACTION REQUIRED for predator population")
            report_lines.append("   • Consider intervention to stabilize prey base")
            report_lines.append("   • Monitor for Allee effects (breeding difficulties at low density)")
        elif pred_score >= 5:
            report_lines.append("⚠️  Enhanced monitoring recommended for predators")
            report_lines.append("   • Stabilize food web dynamics")
    
    if species in ['prey', 'both']:
        if prey_score >= 7:
            report_lines.append("⚠️  URGENT ACTION REQUIRED for prey population")
            report_lines.append("   • Assess predation pressure")
            report_lines.append("   • Evaluate habitat carrying capacity")
    
    report_lines.extend([
        "\n" + "=" * 60,
        "END OF RISK ASSESSMENT",
        "=" * 60
    ])
    
    return [types.TextContent(type="text", text="\n".join(report_lines))]


async def main():
    """Main entry point for the MCP server."""
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
