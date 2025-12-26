#!/usr/bin/env python3
"""
Guardian AI Backend Test Suite

Comprehensive test suite for validating all backend components.
Tests core functionality, API endpoints, and integration scenarios.
"""

import sys
import os
import asyncio
import json
import time
from pathlib import Path
import logging

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestResults:
    """Track test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def pass_test(self, test_name):
        self.passed += 1
        print(f"✓ {test_name}")
    
    def fail_test(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, str(error)))
        print(f"✗ {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"Test Results: {self.passed}/{total} passed")
        
        if self.failed > 0:
            print(f"\nFailed Tests:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        return self.failed == 0

def test_core_imports():
    """Test that all core modules can be imported."""
    
    results = TestResults()
    
    # Test core module imports
    core_modules = [
        ("backend.core.graph_engine", "Graph Engine"),
        ("backend.core.gnn_model", "GNN Model"),
        ("backend.core.risk_calculator", "Risk Calculator"),
        ("backend.core.simulation_engine", "Simulation Engine"),
        ("backend.core.data_loader", "Data Loader"),
        ("backend.core.mitigation_engine", "Mitigation Engine")
    ]
    
    for module_name, display_name in core_modules:
        try:
            __import__(module_name)
            results.pass_test(f"Import {display_name}")
        except Exception as e:
            results.fail_test(f"Import {display_name}", e)
    
    return results

def test_graph_engine():
    """Test graph engine functionality."""
    
    results = TestResults()
    
    try:
        from backend.core.graph_engine import SupplyChainGraph, NodeType, EdgeType
        
        # Create graph
        graph = SupplyChainGraph()
        results.pass_test("Create SupplyChainGraph")
        
        # Add nodes
        graph.add_node("node1", NodeType.VENDOR, tier=1, risk_score=0.3)
        graph.add_node("node2", NodeType.VENDOR, tier=2, risk_score=0.5)
        results.pass_test("Add nodes to graph")
        
        # Add edge
        graph.add_edge("node1", "node2", EdgeType.DEPENDS_ON, "data_flow", strength=0.8)
        results.pass_test("Add edge to graph")
        
        # Test statistics
        stats = graph.get_statistics()
        if stats['node_count'] == 2 and stats['edge_count'] == 1:
            results.pass_test("Graph statistics calculation")
        else:
            results.fail_test("Graph statistics calculation", f"Expected 2 nodes, 1 edge, got {stats}")
        
        # Test export
        cytoscape_data = graph.export_cytoscape_format()
        if 'elements' in cytoscape_data:
            results.pass_test("Cytoscape export")
        else:
            results.fail_test("Cytoscape export", "Missing elements key")
        
    except Exception as e:
        results.fail_test("Graph Engine Test", e)
    
    return results

def test_data_loader():
    """Test data loading functionality."""
    
    results = TestResults()
    
    try:
        from backend.core.data_loader import MERCORDataLoader, create_sample_supply_chain
        
        # Create data loader
        loader = MERCORDataLoader()
        results.pass_test("Create MERCORDataLoader")
        
        # Generate sample supply chain
        graph = create_sample_supply_chain(10)  # Small graph for testing
        results.pass_test("Generate sample supply chain")
        
        # Validate graph
        if len(graph.graph.nodes()) == 10:
            results.pass_test("Sample graph node count")
        else:
            results.fail_test("Sample graph node count", f"Expected 10 nodes, got {len(graph.graph.nodes())}")
        
        if len(graph.graph.edges()) > 0:
            results.pass_test("Sample graph has edges")
        else:
            results.fail_test("Sample graph has edges", "No edges found")
        
    except Exception as e:
        results.fail_test("Data Loader Test", e)
    
    return results

def test_risk_calculator():
    """Test risk calculation functionality."""
    
    results = TestResults()
    
    try:
        from backend.core.risk_calculator import AdvancedRiskCalculator
        from backend.core.data_loader import create_sample_supply_chain
        
        # Create components
        graph = create_sample_supply_chain(10)
        calculator = AdvancedRiskCalculator()
        results.pass_test("Create risk calculator")
        
        # Calculate comprehensive risk
        risk_metrics = calculator.calculate_comprehensive_risk(graph)
        results.pass_test("Calculate comprehensive risk")
        
        # Validate risk metrics
        if 0 <= risk_metrics.overall_score <= 1:
            results.pass_test("Risk score in valid range")
        else:
            results.fail_test("Risk score in valid range", f"Score: {risk_metrics.overall_score}")
        
        # Calculate node risks
        node_risks = calculator.calculate_node_risk_profiles(graph)
        if len(node_risks) == len(graph.graph.nodes()):
            results.pass_test("Node risk profiles count")
        else:
            results.fail_test("Node risk profiles count", f"Expected {len(graph.graph.nodes())}, got {len(node_risks)}")
        
    except Exception as e:
        results.fail_test("Risk Calculator Test", e)
    
    return results

def test_simulation_engine():
    """Test simulation engine functionality."""
    
    results = TestResults()
    
    try:
        from backend.core.simulation_engine import AdvancedSimulationEngine
        from backend.core.data_loader import create_sample_supply_chain
        
        # Create components
        graph = create_sample_supply_chain(10)
        engine = AdvancedSimulationEngine(graph)
        results.pass_test("Create simulation engine")
        
        # Get a node to compromise
        nodes = list(graph.graph.nodes())
        if not nodes:
            results.fail_test("Simulation test", "No nodes available")
            return results
        
        initial_compromised = [nodes[0]]
        
        # Run simulation
        result = engine.run_simulation(initial_compromised)
        results.pass_test("Run simulation")
        
        # Validate result
        if result.total_affected >= 1:
            results.pass_test("Simulation affected nodes")
        else:
            results.fail_test("Simulation affected nodes", f"Expected >= 1, got {result.total_affected}")
        
        if result.blast_radius >= 0:
            results.pass_test("Simulation blast radius")
        else:
            results.fail_test("Simulation blast radius", f"Negative blast radius: {result.blast_radius}")
        
    except Exception as e:
        results.fail_test("Simulation Engine Test", e)
    
    return results

def test_mitigation_engine():
    """Test mitigation engine functionality."""
    
    results = TestResults()
    
    try:
        from backend.core.mitigation_engine import AdvancedMitigationEngine
        from backend.core.data_loader import create_sample_supply_chain
        
        # Create components
        graph = create_sample_supply_chain(10)
        engine = AdvancedMitigationEngine(graph)
        results.pass_test("Create mitigation engine")
        
        # Generate strategies
        strategies = engine.generate_mitigation_strategies(5)
        results.pass_test("Generate mitigation strategies")
        
        # Validate strategies
        if len(strategies) > 0:
            results.pass_test("Mitigation strategies generated")
        else:
            results.fail_test("Mitigation strategies generated", "No strategies returned")
        
        # Validate strategy structure
        if strategies and all('title' in s and 'riskReduction' in s for s in strategies):
            results.pass_test("Mitigation strategy structure")
        else:
            results.fail_test("Mitigation strategy structure", "Missing required fields")
        
    except Exception as e:
        results.fail_test("Mitigation Engine Test", e)
    
    return results

def test_gnn_model():
    """Test GNN model functionality."""
    
    results = TestResults()
    
    try:
        from backend.core.gnn_model import GNNConfig, SupplyChainGNN, GNNInferenceEngine
        
        # Create config and model
        config = GNNConfig()
        model = SupplyChainGNN(config)
        results.pass_test("Create GNN model")
        
        # Test inference engine (with fallback)
        try:
            engine = GNNInferenceEngine("nonexistent_model.pth")  # Should use fallback
            results.pass_test("Create GNN inference engine with fallback")
        except Exception as e:
            results.fail_test("Create GNN inference engine", e)
        
    except Exception as e:
        results.fail_test("GNN Model Test", e)
    
    return results

def test_api_imports():
    """Test API module imports."""
    
    results = TestResults()
    
    try:
        from backend.api.main import app
        results.pass_test("Import FastAPI app")
        
        # Test that app is configured
        if hasattr(app, 'routes') and len(app.routes) > 0:
            results.pass_test("FastAPI routes configured")
        else:
            results.fail_test("FastAPI routes configured", "No routes found")
        
    except Exception as e:
        results.fail_test("API Import Test", e)
    
    return results

async def test_api_endpoints():
    """Test API endpoints (basic functionality)."""
    
    results = TestResults()
    
    try:
        import httpx
        from backend.api.main import app
        
        # Create test client
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            
            # Test health endpoint
            response = await client.get("/health")
            if response.status_code == 200:
                results.pass_test("Health endpoint")
            else:
                results.fail_test("Health endpoint", f"Status: {response.status_code}")
            
            # Test root endpoint
            response = await client.get("/")
            if response.status_code == 200:
                results.pass_test("Root endpoint")
            else:
                results.fail_test("Root endpoint", f"Status: {response.status_code}")
            
            # Test graph export
            response = await client.get("/api/graph/export")
            if response.status_code == 200:
                results.pass_test("Graph export endpoint")
            else:
                results.fail_test("Graph export endpoint", f"Status: {response.status_code}")
            
            # Test risk assessment
            response = await client.get("/api/risk/assessment")
            if response.status_code == 200:
                results.pass_test("Risk assessment endpoint")
            else:
                results.fail_test("Risk assessment endpoint", f"Status: {response.status_code}")
        
    except ImportError:
        results.fail_test("API Endpoint Test", "httpx not available for testing")
    except Exception as e:
        results.fail_test("API Endpoint Test", e)
    
    return results

def test_integration():
    """Test full integration scenario."""
    
    results = TestResults()
    
    try:
        from backend.core import (
            create_sample_supply_chain,
            AdvancedRiskCalculator,
            AdvancedSimulationEngine,
            AdvancedMitigationEngine
        )
        
        # Create supply chain
        graph = create_sample_supply_chain(20)
        results.pass_test("Integration: Create supply chain")
        
        # Initialize all engines
        risk_calculator = AdvancedRiskCalculator()
        simulation_engine = AdvancedSimulationEngine(graph, risk_calculator=risk_calculator)
        mitigation_engine = AdvancedMitigationEngine(graph, risk_calculator=risk_calculator)
        results.pass_test("Integration: Initialize engines")
        
        # Calculate risk
        risk_metrics = risk_calculator.calculate_comprehensive_risk(graph)
        results.pass_test("Integration: Calculate risk")
        
        # Run simulation
        nodes = list(graph.graph.nodes())
        if nodes:
            result = simulation_engine.run_simulation([nodes[0]])
            results.pass_test("Integration: Run simulation")
        
        # Generate mitigations
        strategies = mitigation_engine.generate_mitigation_strategies(3)
        results.pass_test("Integration: Generate mitigations")
        
        # Validate end-to-end flow
        if (risk_metrics.overall_score >= 0 and 
            len(strategies) > 0 and 
            result.total_affected >= 1):
            results.pass_test("Integration: End-to-end validation")
        else:
            results.fail_test("Integration: End-to-end validation", "Invalid results")
        
    except Exception as e:
        results.fail_test("Integration Test", e)
    
    return results

def run_performance_test():
    """Run basic performance tests."""
    
    results = TestResults()
    
    try:
        from backend.core import create_sample_supply_chain, AdvancedRiskCalculator
        
        # Test with larger graph
        start_time = time.time()
        graph = create_sample_supply_chain(100)
        creation_time = time.time() - start_time
        
        if creation_time < 10:  # Should create 100-node graph in under 10 seconds
            results.pass_test(f"Performance: Graph creation ({creation_time:.2f}s)")
        else:
            results.fail_test("Performance: Graph creation", f"Too slow: {creation_time:.2f}s")
        
        # Test risk calculation performance
        calculator = AdvancedRiskCalculator()
        start_time = time.time()
        risk_metrics = calculator.calculate_comprehensive_risk(graph)
        calc_time = time.time() - start_time
        
        if calc_time < 5:  # Should calculate risk in under 5 seconds
            results.pass_test(f"Performance: Risk calculation ({calc_time:.2f}s)")
        else:
            results.fail_test("Performance: Risk calculation", f"Too slow: {calc_time:.2f}s")
        
    except Exception as e:
        results.fail_test("Performance Test", e)
    
    return results

async def main():
    """Run all tests."""
    
    print("🧪 Guardian AI Backend Test Suite")
    print("="*50)
    
    all_results = []
    
    # Core functionality tests
    print("\n📦 Testing Core Imports...")
    all_results.append(test_core_imports())
    
    print("\n🕸️  Testing Graph Engine...")
    all_results.append(test_graph_engine())
    
    print("\n📊 Testing Data Loader...")
    all_results.append(test_data_loader())
    
    print("\n⚠️  Testing Risk Calculator...")
    all_results.append(test_risk_calculator())
    
    print("\n🎯 Testing Simulation Engine...")
    all_results.append(test_simulation_engine())
    
    print("\n🛡️  Testing Mitigation Engine...")
    all_results.append(test_mitigation_engine())
    
    print("\n🧠 Testing GNN Model...")
    all_results.append(test_gnn_model())
    
    print("\n🌐 Testing API Imports...")
    all_results.append(test_api_imports())
    
    print("\n🔗 Testing API Endpoints...")
    all_results.append(await test_api_endpoints())
    
    print("\n🔄 Testing Integration...")
    all_results.append(test_integration())
    
    print("\n⚡ Testing Performance...")
    all_results.append(run_performance_test())
    
    # Summary
    print("\n" + "="*50)
    print("FINAL TEST SUMMARY")
    print("="*50)
    
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total_tests = total_passed + total_failed
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%")
    
    if total_failed > 0:
        print(f"\n❌ {total_failed} tests failed")
        print("Review the errors above and fix the issues.")
        return False
    else:
        print(f"\n✅ All tests passed!")
        print("Guardian AI Backend is ready for deployment.")
        return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)