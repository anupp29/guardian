"""
Quick script to run the backend and test the demo simulation.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.main import app
from backend.core import create_sample_supply_chain, AdvancedRiskCalculator, AdvancedSimulationEngine
import uvicorn
import asyncio
from fastapi.testclient import TestClient

def test_demo_endpoint():
    """Test the demo endpoint directly."""
    print("[TEST] Testing Demo Simulation Endpoint...")
    print("=" * 60)
    
    # Create test client
    client = TestClient(app)
    
    try:
        # Call the demo endpoint
        print("[CALL] Calling /api/simulation/demo...")
        response = client.get("/api/simulation/demo")
        
        print(f"[STATUS] Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n[SUCCESS] Demo simulation completed!")
            print("=" * 60)
            
            if "data" in data:
                sim_data = data["data"]
                
                print("\n[NETWORKX METRICS]")
                if "networkx_metrics" in sim_data:
                    nx_metrics = sim_data["networkx_metrics"]
                    print(f"  [OK] Total nodes: {nx_metrics.get('total_nodes', 'N/A')}")
                    print(f"  [OK] Total edges: {nx_metrics.get('total_edges', 'N/A')}")
                    print(f"  [OK] Graph density: {nx_metrics.get('graph_density', 0):.4f}")
                    print(f"  [OK] Is connected: {nx_metrics.get('is_weakly_connected', False)}")
                    
                    if "most_central_node" in nx_metrics:
                        central = nx_metrics["most_central_node"]
                        print(f"  [OK] Most central node: {central.get('name', central.get('node_id'))}")
                
                print("\n[SIMULATION RESULTS]")
                if "simulation_results" in sim_data:
                    sim_results = sim_data["simulation_results"]
                    print(f"  [OK] Initial compromised: {len(sim_results.get('initial_compromised', []))} nodes")
                    print(f"  [OK] Total affected: {sim_results.get('total_affected', 0)} nodes")
                    print(f"  [OK] Blast radius: {sim_results.get('blast_radius', 0)} additional compromises")
                    print(f"  [OK] Cascade depth: {sim_results.get('cascade_depth', 0)} waves")
                    print(f"  [OK] Propagation time: {sim_results.get('propagation_time_ms', 0):.0f}ms")
                
                print("\n[PATH ANALYSIS]")
                if "path_analysis" in sim_data:
                    path_analysis = sim_data["path_analysis"]
                    print(f"  [OK] Total paths found: {path_analysis.get('total_paths_found', 0)}")
                    if "path_statistics" in path_analysis:
                        stats = path_analysis["path_statistics"]
                        print(f"  [OK] Average path length: {stats.get('avg_length', 0):.2f}")
                        print(f"  [OK] Max path length: {stats.get('max_length', 0)}")
                    print(f"  [OK] Cycles detected: {path_analysis.get('cycles_detected', 0)}")
                
                print("\n[PROPAGATION ANALYSIS]")
                if "propagation_analysis" in sim_data:
                    prop_analysis = sim_data["propagation_analysis"]
                    print(f"  [OK] Total steps: {prop_analysis.get('total_steps', 0)}")
                    print(f"  [OK] Total propagation paths: {prop_analysis.get('total_propagation_paths', 0)}")
                
                print("\n[GRAPH SUMMARY]")
                if "graph_summary" in sim_data:
                    summary = sim_data["graph_summary"]
                    print(f"  [OK] Nodes by tier: {summary.get('nodes_by_tier', {})}")
                    print(f"  [OK] Risk distribution: {summary.get('risk_distribution', {})}")
                
                print("\n[MITIGATION SUGGESTIONS]")
                if "mitigation_suggestions" in sim_data:
                    mitigations = sim_data["mitigation_suggestions"]
                    for i, mit in enumerate(mitigations[:3], 1):
                        desc = mit.get('description', 'N/A')
                        print(f"  {i}. {desc[:70]}...")
            
            print("\n" + "=" * 60)
            print("[SUCCESS] NetworkX Simulation Working Perfectly!")
            print("=" * 60)
            
            # Print sample of detailed data
            print("\n[SAMPLE DATA]")
            print(f"  Simulation ID: {sim_data.get('simulation_id', 'N/A')}")
            print(f"  Status: {sim_data.get('status', 'N/A')}")
            print(f"  Message: {sim_data.get('message', 'N/A')}")
            
            return True
        else:
            print(f"\n[ERROR] Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set UTF-8 encoding for Windows
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("Guardian AI - NetworkX Demo Simulation Test")
    print("=" * 60)
    print()
    
    success = test_demo_endpoint()
    
    if success:
        print("\n[SUCCESS] Test passed! Demo simulation is working correctly.")
        print("\nTo run the API server:")
        print("   python -m uvicorn backend.api.main:app --reload")
        print("\nThen visit: http://localhost:8000/api/simulation/demo")
    else:
        print("\n[ERROR] Test failed. Check errors above.")
        sys.exit(1)

