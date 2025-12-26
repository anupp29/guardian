"""
Test script to verify guardian/v2 works locally
Tests imports, agent instantiation, and basic functionality
"""

import sys
import os
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all imports work correctly"""
    print("=" * 70)
    print("Testing Imports...")
    print("=" * 70)
    
    tests = []
    
    try:
        from agents.registry import AgentRegistry, get_registry
        tests.append(("[OK]", "Registry imports"))
    except Exception as e:
        tests.append(("[FAIL]", f"Registry imports: {e}"))
        return False
    
    try:
        from agents.orchestrator import OrchestratorAgent, OrchestratorInput, OrchestratorOutput
        tests.append(("[OK]", "Orchestrator imports"))
    except Exception as e:
        tests.append(("[FAIL]", f"Orchestrator imports: {e}"))
        return False
    
    try:
        from agents.simulation import SimulationAgent, SimulationInput, SimulationOutput
        tests.append(("[OK]", "Simulation imports"))
    except Exception as e:
        tests.append(("[FAIL]", f"Simulation imports: {e}"))
        return False
    
    try:
        from agents.impact_reasoning import ImpactReasoningAgent, ImpactReasoningInput
        tests.append(("[OK]", "ImpactReasoning imports"))
    except Exception as e:
        tests.append(("[FAIL]", f"ImpactReasoning imports: {e}"))
        return False
    
    try:
        from agents.mitigation import MitigationAgent, MitigationInput, MitigationOutput
        tests.append(("[OK]", "Mitigation imports"))
    except Exception as e:
        tests.append(("[FAIL]", f"Mitigation imports: {e}"))
        return False
    
    for status, msg in tests:
        print(f"{status} {msg}")
    
    return all("[OK]" in t[0] for t in tests)

def test_agent_instantiation():
    """Test that agents can be instantiated"""
    print("\n" + "=" * 70)
    print("Testing Agent Instantiation...")
    print("=" * 70)
    
    tests = []
    
    try:
        from agents.registry import get_registry
        registry = get_registry()
        tests.append(("[OK]", "Registry instantiation"))
    except Exception as e:
        tests.append(("[FAIL]", f"Registry instantiation: {e}"))
        traceback.print_exc()
        return False
    
    try:
        from agents.simulation import SimulationAgent
        sim_agent = SimulationAgent()
        tests.append(("[OK]", "SimulationAgent instantiation"))
    except Exception as e:
        tests.append(("[FAIL]", f"SimulationAgent instantiation: {e}"))
        traceback.print_exc()
        return False
    
    try:
        from agents.impact_reasoning import ImpactReasoningAgent
        impact_agent = ImpactReasoningAgent()
        tests.append(("[OK]", "ImpactReasoningAgent instantiation"))
    except Exception as e:
        tests.append(("[FAIL]", f"ImpactReasoningAgent instantiation: {e}"))
        traceback.print_exc()
        return False
    
    try:
        from agents.mitigation import MitigationAgent
        mit_agent = MitigationAgent()
        tests.append(("[OK]", "MitigationAgent instantiation"))
    except Exception as e:
        tests.append(("[FAIL]", f"MitigationAgent instantiation: {e}"))
        traceback.print_exc()
        return False
    
    try:
        from agents.orchestrator import OrchestratorAgent
        orch_agent = OrchestratorAgent()
        tests.append(("[OK]", "OrchestratorAgent instantiation"))
    except Exception as e:
        tests.append(("[FAIL]", f"OrchestratorAgent instantiation: {e}"))
        traceback.print_exc()
        return False
    
    for status, msg in tests:
        print(f"{status} {msg}")
    
    return all("[OK]" in t[0] for t in tests)

def test_basic_functionality():
    """Test basic functionality without requiring API keys"""
    print("\n" + "=" * 70)
    print("Testing Basic Functionality...")
    print("=" * 70)
    
    tests = []
    
    try:
        from agents.simulation import SimulationAgent, SimulationInput
        sim_agent = SimulationAgent()
        
        # Test with sample data
        test_input = {
            "vendor_id": "VENDOR_001",
            "max_depth": 2,
            "graph_metadata": None
        }
        
        result = sim_agent.run(test_input)
        
        if isinstance(result, dict) and "source_vendor_id" in result:
            tests.append(("[OK]", "SimulationAgent.run() - basic execution"))
        else:
            tests.append(("[FAIL]", f"SimulationAgent.run() - unexpected result: {type(result)}"))
    except Exception as e:
        tests.append(("[FAIL]", f"SimulationAgent.run() - {e}"))
        traceback.print_exc()
    
    try:
        from agents.registry import get_registry
        registry = get_registry()
        agents = registry.list_agents()
        
        if len(agents) == 4 and "SimulationAgent" in agents:
            tests.append(("[OK]", "Registry.list_agents()"))
        else:
            tests.append(("[FAIL]", f"Registry.list_agents() - got: {agents}"))
    except Exception as e:
        tests.append(("[FAIL]", f"Registry.list_agents() - {e}"))
        traceback.print_exc()
    
    try:
        from agents.registry import get_registry
        registry = get_registry()
        agent = registry.get_agent("SimulationAgent")
        
        if agent is not None:
            tests.append(("[OK]", "Registry.get_agent()"))
        else:
            tests.append(("[FAIL]", "Registry.get_agent() - returned None"))
    except Exception as e:
        tests.append(("[FAIL]", f"Registry.get_agent() - {e}"))
        traceback.print_exc()
    
    for status, msg in tests:
        print(f"{status} {msg}")
    
    return all("[OK]" in t[0] for t in tests)

def test_schema_validation():
    """Test that schemas work correctly"""
    print("\n" + "=" * 70)
    print("Testing Schema Validation...")
    print("=" * 70)
    
    tests = []
    
    try:
        from agents.orchestrator import OrchestratorInput
        input_data = OrchestratorInput(
            vendor_id="VENDOR_001",
            max_depth=3
        )
        if input_data.vendor_id == "VENDOR_001" and input_data.max_depth == 3:
            tests.append(("[OK]", "OrchestratorInput schema validation"))
        else:
            tests.append(("[FAIL]", "OrchestratorInput schema validation - values incorrect"))
    except Exception as e:
        tests.append(("[FAIL]", f"OrchestratorInput schema validation - {e}"))
        traceback.print_exc()
    
    try:
        from agents.simulation import SimulationInput
        input_data = SimulationInput(
            vendor_id="VENDOR_001",
            max_depth=2
        )
        if input_data.vendor_id == "VENDOR_001":
            tests.append(("[OK]", "SimulationInput schema validation"))
        else:
            tests.append(("[FAIL]", "SimulationInput schema validation - values incorrect"))
    except Exception as e:
        tests.append(("[FAIL]", f"SimulationInput schema validation - {e}"))
        traceback.print_exc()
    
    for status, msg in tests:
        print(f"{status} {msg}")
    
    return all("[OK]" in t[0] for t in tests)

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("Guardian v2 Local Testing")
    print("=" * 70)
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Agent Instantiation", test_agent_instantiation()))
    results.append(("Schema Validation", test_schema_validation()))
    results.append(("Basic Functionality", test_basic_functionality()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed! Guardian v2 is working correctly.")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Check output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

