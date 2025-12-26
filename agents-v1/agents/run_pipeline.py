"""
Guardian AI Pipeline Runner
Executes the full agent pipeline: Orchestrator → Simulation → Impact → Mitigation
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

from .orchestrator.agent import OrchestratorAgent
from .orchestrator.schema import OrchestratorInput


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('guardian_ai.log')
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print Guardian AI banner"""
    banner = """
================================================================================
  GUARDIAN AI - SUPPLY CHAIN RISK SIMULATION
  Multi-Agent Decision Support System using Google ADK
================================================================================
"""
    print(banner)


def print_results(output: dict):
    """Pretty print pipeline results"""
    print("\n" + "=" * 80)
    print("EXECUTION RESULTS")
    print("=" * 80)
    
    if not output.get('success'):
        print(f"\n[ERROR] Pipeline failed: {output.get('error_message', 'Unknown error')}")
        return
    
    print("\n[SUCCESS] Pipeline executed successfully")
    
    # Execution trace
    print("\n" + "-" * 80)
    print("EXECUTION TRACE")
    print("-" * 80)
    for i, trace in enumerate(output.get('execution_trace', []), 1):
        print(f"\n[{i}] {trace['agent_name']}")
        print(f"    Input: {trace['input_summary']}")
        print(f"    Output: {trace['output_summary']}")
        if trace.get('execution_time_ms'):
            print(f"    Time: {trace['execution_time_ms']:.2f}ms")
    
    # Simulation results
    sim_results = output.get('simulation_results')
    if sim_results:
        print("\n" + "-" * 80)
        print("SIMULATION RESULTS")
        print("-" * 80)
        print(f"Source Vendor: {sim_results.get('source_vendor_id')}")
        print(f"Total Affected Nodes: {sim_results.get('total_affected_nodes', 0)}")
        print(f"Propagation Paths: {len(sim_results.get('propagation_paths', []))}")
        metrics = sim_results.get('metrics', {})
        print(f"Average Path Length: {metrics.get('average_path_length', 0):.2f}")
        print(f"Max Path Length: {metrics.get('max_path_length', 0)}")
    
    # Impact explanations
    impact_explanations = output.get('impact_explanations', [])
    if impact_explanations:
        print("\n" + "-" * 80)
        print("IMPACT EXPLANATIONS")
        print("-" * 80)
        for i, exp in enumerate(impact_explanations[:5], 1):  # Show top 5
            path_str = ' -> '.join(exp.get('path', []))  # Use ASCII arrow
            print(f"\n[{i}] Path: {path_str}")
            print(f"    Cause: {exp.get('cause', 'N/A')}")
            print(f"    Effect: {exp.get('effect', 'N/A')}")
            if exp.get('business_impact'):
                print(f"    Business Impact: {exp.get('business_impact')}")
        if len(impact_explanations) > 5:
            print(f"\n... and {len(impact_explanations) - 5} more explanations")
    
    # Mitigation recommendations
    mitigations = output.get('mitigation_recommendations', [])
    if mitigations:
        print("\n" + "-" * 80)
        print("MITIGATION RECOMMENDATIONS")
        print("-" * 80)
        for i, mit in enumerate(mitigations[:5], 1):  # Show top 5
            print(f"\n[{i}] {mit.get('description', 'N/A')}")
            print(f"    Risk Reduction: {mit.get('risk_reduction', 0):.2%}")
            print(f"    Paths Eliminated: {mit.get('affected_paths_reduced', 0)}")
            print(f"    Complexity: {mit.get('implementation_complexity', 'N/A')}")
            if mit.get('trade_offs'):
                print(f"    Trade-offs: {mit.get('trade_offs')}")
        if len(mitigations) > 5:
            print(f"\n... and {len(mitigations) - 5} more recommendations")
    
    print("\n" + "=" * 80)


def main():
    """Main pipeline execution"""
    parser = argparse.ArgumentParser(
        description="Guardian AI - Supply Chain Risk Simulation Pipeline"
    )
    parser.add_argument(
        'vendor_id',
        nargs='?',
        default='VENDOR_001',
        help='Starting vendor ID for simulation (default: VENDOR_001)'
    )
    parser.add_argument(
        'max_depth',
        nargs='?',
        type=int,
        default=3,
        help='Maximum propagation depth (default: 3)'
    )
    parser.add_argument(
        '--graph-file',
        type=str,
        help='Optional JSON file with graph metadata'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        help='Output JSON file path (default: guardian_output_<vendor_id>.json)'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Load graph metadata if provided
    graph_metadata = None
    if args.graph_file:
        try:
            with open(args.graph_file, 'r') as f:
                graph_metadata = json.load(f)
            logger.info(f"Loaded graph metadata from {args.graph_file}")
        except Exception as e:
            logger.warning(f"Failed to load graph file: {e}, using default graph")
    
    # Create orchestrator input
    orchestrator_input = OrchestratorInput(
        vendor_id=args.vendor_id,
        max_depth=args.max_depth,
        graph_metadata=graph_metadata
    )
    
    logger.info(f"Starting pipeline: vendor_id={args.vendor_id}, max_depth={args.max_depth}")
    
    # Execute pipeline
    try:
        orchestrator = OrchestratorAgent()
        output = orchestrator.run(orchestrator_input)
        
        # Convert to dict for JSON serialization
        output_dict = output.model_dump() if hasattr(output, 'model_dump') else output
        
        # Print results
        print_results(output_dict)
        
        # Save output
        output_file = args.output_file or f"guardian_output_{args.vendor_id}.json"
        with open(output_file, 'w') as f:
            json.dump(output_dict, f, indent=2, default=str)
        print(f"\n[SAVED] Results saved to: {output_file}")
        
        return 0 if output_dict.get('success') else 1
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        print(f"\n[ERROR] Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

