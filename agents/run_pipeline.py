"""
Guardian AI - Pipeline Runner

Executable script to run the full Guardian AI pipeline.
Demonstrates the complete agent orchestration flow.
"""

import logging
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.registry import create_registry
from agents.orchestrator.schema import OrchestratorInput


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('guardian_ai.log')
    ]
)

logger = logging.getLogger(__name__)


def print_separator(title: str = ""):
    """Print a visual separator."""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


def print_json(data: dict, title: str = ""):
    """Pretty print JSON data."""
    if title:
        print(f"\n{title}:")
    print(json.dumps(data, indent=2))


def run_pipeline(vendor_id: str, max_depth: int = 5):
    """Run the full Guardian AI pipeline."""
    print_separator("GUARDIAN AI - SUPPLY CHAIN RISK SIMULATION")
    
    logger.info("Starting Guardian AI pipeline")
    logger.info(f"Vendor ID: {vendor_id}")
    logger.info(f"Max Depth: {max_depth}")
    
    # Initialize registry (with optional Google API key from environment)
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        logger.info("Using Google API key from environment")
    else:
        logger.warning("No GOOGLE_API_KEY found - using fallback reasoning")
    
    registry = create_registry(google_api_key=api_key)
    orchestrator = registry.get_orchestrator()
    
    # Prepare input (simplified - no GraphMetadata)
    input_data = OrchestratorInput(
        vendor_id=vendor_id,
        max_depth=max_depth
    )
    
    print_separator("INPUT")
    print_json(input_data.model_dump())
    
    # Execute pipeline
    print_separator("EXECUTING PIPELINE")
    output = orchestrator.run(input_data)
    
    # Display results
    print_separator("EXECUTION TRACE")
    for trace_item in output.trace:
        print(f"[{trace_item.execution_order}] {trace_item.agent_name}")
        print(f"    Input: {trace_item.input_summary}")
        print(f"    Output: {trace_item.output_summary}")
        print()
    
    print_separator("SIMULATION RESULTS")
    sim_results = output.simulation_results
    print(f"Source Vendor: {sim_results['source_vendor_id']}")
    print(f"Propagation Paths: {len(sim_results['propagation_paths'])}")
    print(f"Affected Nodes: {len(sim_results['affected_node_ids'])}")
    print(f"\nMetrics:")
    print(f"  Total Affected: {sim_results['metrics']['total_affected_nodes']}")
    print(f"  Max Fan-out: {sim_results['metrics']['max_fan_out']}")
    print(f"  Avg Path Length: {sim_results['metrics']['average_path_length']}")
    
    # Show sample paths
    print(f"\nSample Propagation Paths (showing first 5):")
    for i, path_data in enumerate(sim_results['propagation_paths'][:5], 1):
        path_str = " → ".join(path_data['path'])
        print(f"  {i}. {path_str} (length: {path_data['length']})")
    
    print_separator("IMPACT ANALYSIS")
    impact_results = output.impact_analysis
    print(f"Summary: {impact_results['summary']}\n")
    
    print(f"Impact Explanations (showing first 3):")
    for i, exp in enumerate(impact_results['explanations'][:3], 1):
        print(f"\n{i}. Path: {' → '.join(exp['path'])}")
        print(f"   Cause: {exp['cause']}")
        print(f"   Effect: {exp['effect']}")
        if exp.get('uncertainty_notes'):
            print(f"   ⚠️  Uncertainty: {exp['uncertainty_notes']}")
    
    if impact_results['data_limitations']:
        print(f"\nData Limitations:")
        for limitation in impact_results['data_limitations']:
            print(f"  • {limitation}")
    
    print_separator("MITIGATION RECOMMENDATIONS")
    mitigation_results = output.mitigations
    print(f"Baseline Paths: {mitigation_results['total_paths_before']}")
    print(f"Methodology: {mitigation_results['methodology']}\n")
    
    print(f"Top Mitigations (showing first 5):")
    for i, action in enumerate(mitigation_results['ranked_mitigations'][:5], 1):
        print(f"\n{i}. {action['action_type'].upper()}: {action['target']}")
        print(f"   {action['description']}")
        print(f"   Risk Reduction: {action['risk_reduction']:.1%}")
        print(f"   Paths Reduced: {action['affected_paths_reduced']}")
    
    print_separator("PIPELINE COMPLETE")
    
    # Save full output to file
    output_file = f"guardian_output_{vendor_id}.json"
    with open(output_file, 'w') as f:
        json.dump(output.model_dump(), f, indent=2)
    
    print(f"✅ Full output saved to: {output_file}")
    logger.info(f"Pipeline execution complete - output saved to {output_file}")


def main():
    """Main entry point."""
    # Parse command-line arguments
    if len(sys.argv) > 1:
        vendor_id = sys.argv[1]
    else:
        vendor_id = "VENDOR_001"  # Default
    
    if len(sys.argv) > 2:
        max_depth = int(sys.argv[2])
    else:
        max_depth = 5  # Default
    
    try:
        run_pipeline(vendor_id=vendor_id, max_depth=max_depth)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
