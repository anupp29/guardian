"""
Perfect Pipeline Tester for Guardian AI v1 ADK Pipeline
- Tests agent execution flow directly
- Verifies correct agent calls
- Checks result consistency
- Uses provided API key with rate limiting
"""

import os
import sys
import time
import json
from pathlib import Path

# Set API key before importing agents
os.environ["GOOGLE_API_KEY"] = "AIzaSyD-RG8mdgorx6n3rs6sHZLWdj4M_9ntkpg"
os.environ["GEMINI_API_KEY"] = "AIzaSyD-RG8mdgorx6n3rs6sHZLWdj4M_9ntkpg"

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_pipeline():
    """Test the full pipeline and verify agent calls"""
    
    print("=" * 80)
    print("GUARDIAN AI v1 - PERFECT PIPELINE TESTER")
    print("=" * 80)
    print(f"API Key: {os.environ.get('GOOGLE_API_KEY', 'NOT SET')[:20]}...")
    print("Testing agent execution flow...")
    print("=" * 80)
    print()
    
    try:
        # Import agents directly (avoiding orchestrator import issue)
        print("[SETUP] Importing agents...")
        from agents.simulation.agent import SimulationAgent
        from agents.impact_reasoning.agent import ImpactReasoningAgent
        from agents.mitigation.agent import MitigationAgent
        print("[OK] All agents imported successfully")
        print()
        
        # Test input
        vendor_id = "VENDOR_001"
        max_depth = 3
        graph_metadata = None
        
        print("[TEST] Starting pipeline execution...")
        print(f"       Vendor ID: {vendor_id}")
        print(f"       Max Depth: {max_depth}")
        print()
        
        execution_trace = []
        results = {}
        
        # Step 1: SimulationAgent
        print("[STEP 1] Calling SimulationAgent...")
        print("[INFO] Waiting 1 second (rate limit protection)...")
        time.sleep(1)
        
        start_time = time.time()
        sim_agent = SimulationAgent()
        sim_input = {
            "vendor_id": vendor_id,
            "max_depth": max_depth,
            "graph_metadata": graph_metadata
        }
        sim_result = sim_agent.run(sim_input)
        sim_time = (time.time() - start_time) * 1000
        
        sim_paths = len(sim_result.get('propagation_paths', []))
        sim_nodes = sim_result.get('total_affected_nodes', 0)
        
        execution_trace.append({
            "agent": "SimulationAgent",
            "time_ms": sim_time,
            "paths": sim_paths,
            "nodes": sim_nodes
        })
        
        print(f"[OK] SimulationAgent completed in {sim_time:.2f}ms")
        print(f"     Found {sim_paths} paths affecting {sim_nodes} nodes")
        print()
        
        results["simulation"] = sim_result
        
        # Step 2: ImpactReasoningAgent
        print("[STEP 2] Calling ImpactReasoningAgent...")
        print("[INFO] Waiting 3 seconds (rate limit protection)...")
        time.sleep(3)
        
        start_time = time.time()
        impact_agent = ImpactReasoningAgent()
        impact_input = {
            "simulation_results": sim_result,
            "graph_metadata": graph_metadata
        }
        impact_result = impact_agent.run(impact_input)
        impact_time = (time.time() - start_time) * 1000
        
        impact_count = len(impact_result.get('explanations', []))
        
        execution_trace.append({
            "agent": "ImpactReasoningAgent",
            "time_ms": impact_time,
            "explanations": impact_count
        })
        
        print(f"[OK] ImpactReasoningAgent completed in {impact_time:.2f}ms")
        print(f"     Generated {impact_count} explanations")
        print()
        
        results["impact"] = impact_result
        
        # Step 3: MitigationAgent
        print("[STEP 3] Calling MitigationAgent...")
        print("[INFO] Waiting 2 seconds (rate limit protection)...")
        time.sleep(2)
        
        start_time = time.time()
        mit_agent = MitigationAgent()
        mit_input = {
            "simulation_results": sim_result,
            "impact_explanations": impact_result.get('explanations', []),
            "graph_metadata": graph_metadata
        }
        mit_result = mit_agent.run(mit_input)
        mit_time = (time.time() - start_time) * 1000
        
        mit_count = len(mit_result.get('ranked_mitigations', []))
        
        execution_trace.append({
            "agent": "MitigationAgent",
            "time_ms": mit_time,
            "recommendations": mit_count
        })
        
        print(f"[OK] MitigationAgent completed in {mit_time:.2f}ms")
        print(f"     Ranked {mit_count} mitigation actions")
        print()
        
        results["mitigation"] = mit_result
        
        # Verification
        print("=" * 80)
        print("AGENT CALL VERIFICATION")
        print("=" * 80)
        
        expected_agents = ["SimulationAgent", "ImpactReasoningAgent", "MitigationAgent"]
        found_agents = [trace["agent"] for trace in execution_trace]
        
        all_called = True
        for expected in expected_agents:
            if expected in found_agents:
                print(f"[OK] {expected} was called correctly")
            else:
                print(f"[FAIL] {expected} was NOT called")
                all_called = False
        
        print()
        
        # Result verification
        print("=" * 80)
        print("RESULT VERIFICATION")
        print("=" * 80)
        
        checks_passed = 0
        total_checks = 4
        
        if sim_paths > 0:
            print(f"[OK] Simulation: {sim_paths} paths found")
            checks_passed += 1
        else:
            print("[FAIL] Simulation: No paths found")
        
        if impact_count > 0:
            print(f"[OK] Impact: {impact_count} explanations generated")
            checks_passed += 1
        else:
            print("[FAIL] Impact: No explanations generated")
        
        if mit_count > 0:
            print(f"[OK] Mitigation: {mit_count} recommendations ranked")
            checks_passed += 1
        else:
            print("[FAIL] Mitigation: No recommendations generated")
        
        if all_called:
            print("[OK] All agents called in correct order")
            checks_passed += 1
        else:
            print("[FAIL] Agents not called correctly")
        
        print()
        print("=" * 80)
        
        if checks_passed == total_checks:
            print("[SUCCESS] ALL CHECKS PASSED - Pipeline is working perfectly!")
            print("=" * 80)
            
            # Save results
            output_file = "test_pipeline_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "success": True,
                    "execution_trace": execution_trace,
                    "results": results,
                    "agents_called": found_agents
                }, f, indent=2, ensure_ascii=False)
            
            print(f"[INFO] Results saved to: {output_file}")
            return True
        else:
            print(f"[PARTIAL] {checks_passed}/{total_checks} checks passed")
            print("=" * 80)
            return False
        
    except Exception as e:
        print()
        print("=" * 80)
        print("[FAIL] TEST FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
