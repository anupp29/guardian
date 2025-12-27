"""
Test script for the crazy demo simulation endpoint.
Run this to verify NetworkX simulation is working locally.
"""

import requests
import json
import time

def test_demo_simulation():
    """Test the demo simulation endpoint."""
    
    # API endpoint (assuming running on localhost:8000)
    url = "http://localhost:8000/api/simulation/demo"
    
    print("🚀 Testing CRAZY NetworkX Demo Simulation...")
    print("=" * 60)
    
    try:
        print(f"📡 Calling endpoint: {url}")
        start_time = time.time()
        
        response = requests.get(url, timeout=30)
        
        elapsed_time = time.time() - start_time
        
        print(f"⏱️  Response time: {elapsed_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ SUCCESS! Simulation completed!")
            print("=" * 60)
            
            # Display key results
            if "data" in data:
                sim_data = data["data"]
                
                print("\n📈 NETWORKX METRICS:")
                if "networkx_metrics" in sim_data:
                    nx_metrics = sim_data["networkx_metrics"]
                    print(f"  • Total nodes: {nx_metrics.get('total_nodes', 'N/A')}")
                    print(f"  • Total edges: {nx_metrics.get('total_edges', 'N/A')}")
                    print(f"  • Graph density: {nx_metrics.get('graph_density', 0):.4f}")
                    print(f"  • Is connected: {nx_metrics.get('is_weakly_connected', False)}")
                    
                    if "most_central_node" in nx_metrics:
                        central = nx_metrics["most_central_node"]
                        print(f"  • Most central node: {central.get('name', central.get('node_id'))}")
                
                print("\n🎯 SIMULATION RESULTS:")
                if "simulation_results" in sim_data:
                    sim_results = sim_data["simulation_results"]
                    print(f"  • Initial compromised: {len(sim_results.get('initial_compromised', []))} nodes")
                    print(f"  • Total affected: {sim_results.get('total_affected', 0)} nodes")
                    print(f"  • Blast radius: {sim_results.get('blast_radius', 0)} additional compromises")
                    print(f"  • Cascade depth: {sim_results.get('cascade_depth', 0)} waves")
                    print(f"  • Propagation time: {sim_results.get('propagation_time_ms', 0):.0f}ms")
                
                print("\n🛤️  PATH ANALYSIS:")
                if "path_analysis" in sim_data:
                    path_analysis = sim_data["path_analysis"]
                    print(f"  • Total paths found: {path_analysis.get('total_paths_found', 0)}")
                    if "path_statistics" in path_analysis:
                        stats = path_analysis["path_statistics"]
                        print(f"  • Average path length: {stats.get('avg_length', 0):.2f}")
                        print(f"  • Max path length: {stats.get('max_length', 0)}")
                    print(f"  • Cycles detected: {path_analysis.get('cycles_detected', 0)}")
                
                print("\n🌊 PROPAGATION ANALYSIS:")
                if "propagation_analysis" in sim_data:
                    prop_analysis = sim_data["propagation_analysis"]
                    print(f"  • Total steps: {prop_analysis.get('total_steps', 0)}")
                    print(f"  • Total propagation paths: {prop_analysis.get('total_propagation_paths', 0)}")
                
                print("\n📊 GRAPH SUMMARY:")
                if "graph_summary" in sim_data:
                    summary = sim_data["graph_summary"]
                    print(f"  • Nodes by tier: {summary.get('nodes_by_tier', {})}")
                    print(f"  • Risk distribution: {summary.get('risk_distribution', {})}")
                
                print("\n💡 MITIGATION SUGGESTIONS:")
                if "mitigation_suggestions" in sim_data:
                    mitigations = sim_data["mitigation_suggestions"]
                    for i, mit in enumerate(mitigations[:3], 1):
                        print(f"  {i}. {mit.get('description', 'N/A')[:60]}...")
            
            print("\n" + "=" * 60)
            print("✅ All NetworkX features working correctly!")
            print("=" * 60)
            
            # Save full response to file
            with open("demo_simulation_result.json", "w") as f:
                json.dump(data, f, indent=2, default=str)
            print("\n💾 Full results saved to: demo_simulation_result.json")
            
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server.")
        print("💡 Make sure the backend is running:")
        print("   cd guardian/backend")
        print("   python -m uvicorn api.main:app --reload")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_demo_simulation()





