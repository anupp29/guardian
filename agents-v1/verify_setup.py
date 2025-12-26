"""
Verification script to test Guardian AI v1 setup
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all modules can be imported"""
    logger.info("Testing imports...")
    
    try:
        from agents.registry import AgentRegistry
        logger.info("✅ AgentRegistry imported")
    except Exception as e:
        logger.error(f"❌ Failed to import AgentRegistry: {e}")
        return False
    
    try:
        from agents.orchestrator.agent import OrchestratorAgent
        logger.info("✅ OrchestratorAgent imported")
    except Exception as e:
        logger.error(f"❌ Failed to import OrchestratorAgent: {e}")
        return False
    
    try:
        from agents.simulation.agent import SimulationAgent
        logger.info("✅ SimulationAgent imported")
    except Exception as e:
        logger.error(f"❌ Failed to import SimulationAgent: {e}")
        return False
    
    try:
        from agents.impact_reasoning.agent import ImpactReasoningAgent
        logger.info("✅ ImpactReasoningAgent imported")
    except Exception as e:
        logger.error(f"❌ Failed to import ImpactReasoningAgent: {e}")
        return False
    
    try:
        from agents.mitigation.agent import MitigationAgent
        logger.info("✅ MitigationAgent imported")
    except Exception as e:
        logger.error(f"❌ Failed to import MitigationAgent: {e}")
        return False
    
    return True


def test_registry():
    """Test agent registry"""
    logger.info("\nTesting agent registry...")
    
    try:
        from agents.registry import get_registry
        registry = get_registry()
        agents = registry.list_agents()
        logger.info(f"✅ Registry initialized with {len(agents)} agents: {agents}")
        
        # Test getting each agent
        for agent_name in agents:
            agent = registry.get_agent(agent_name)
            logger.info(f"✅ Retrieved {agent_name}: {type(agent).__name__}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simulation_agent():
    """Test SimulationAgent with sample input"""
    logger.info("\nTesting SimulationAgent...")
    
    try:
        from agents.simulation.agent import SimulationAgent
        agent = SimulationAgent()
        
        test_input = {
            "vendor_id": "VENDOR_001",
            "max_depth": 3
        }
        
        result = agent.run(test_input)
        
        if result and 'propagation_paths' in result:
            logger.info(f"✅ SimulationAgent executed successfully")
            logger.info(f"   Found {len(result['propagation_paths'])} paths")
            logger.info(f"   Affected {result['total_affected_nodes']} nodes")
            return True
        else:
            logger.error(f"❌ SimulationAgent returned invalid result")
            return False
            
    except Exception as e:
        logger.error(f"❌ SimulationAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    logger.info("=" * 60)
    logger.info("Guardian AI v1 - Setup Verification")
    logger.info("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Registry", test_registry()))
    results.append(("SimulationAgent", test_simulation_agent()))
    
    logger.info("\n" + "=" * 60)
    logger.info("Verification Summary")
    logger.info("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        logger.info("\n🎉 All tests passed! Guardian AI v1 is ready to use.")
        logger.info("\nNext steps:")
        logger.info("  python -m agents.run_pipeline VENDOR_001 3")
        return 0
    else:
        logger.error("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

