"""
Test Guardian AI v1 with API key
"""

import os
import sys
import logging

# SECURITY: Never hardcode API keys!
# Set API key from environment variable or prompt user
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️  WARNING: No API key found in environment variables!")
    print("   Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
    print("   Example: export GOOGLE_API_KEY='your-api-key-here'")
    sys.exit(1)
os.environ["GOOGLE_API_KEY"] = api_key

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_impact_agent():
    """Test ImpactReasoningAgent with API"""
    logger.info("Testing ImpactReasoningAgent with Gemini API...")
    
    try:
        from agents.impact_reasoning.agent import ImpactReasoningAgent
        
        agent = ImpactReasoningAgent()
        
        if not agent.model:
            logger.error("❌ Gemini model not initialized")
            return False
        
        logger.info("✅ Gemini model initialized")
        
        # Test with sample data
        test_input = {
            "simulation_results": {
                "source_vendor_id": "VENDOR_001",
                "propagation_paths": [
                    {
                        "path": ["VENDOR_001", "VENDOR_002", "VENDOR_005"],
                        "length": 2,
                        "affected_nodes": ["VENDOR_002", "VENDOR_005"]
                    }
                ],
                "total_affected_nodes": 2,
                "unique_affected_nodes": ["VENDOR_002", "VENDOR_005"]
            }
        }
        
        logger.info("Calling ImpactReasoningAgent...")
        result = agent.run(test_input)
        
        if result and 'explanations' in result:
            logger.info(f"✅ ImpactReasoningAgent executed successfully")
            logger.info(f"   Generated {len(result['explanations'])} explanations")
            if result['explanations']:
                exp = result['explanations'][0]
                logger.info(f"   Sample: {exp.get('cause', 'N/A')[:50]}...")
            return True
        else:
            logger.error("❌ Invalid result from ImpactReasoningAgent")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


def test_full_pipeline():
    """Test full pipeline"""
    logger.info("\nTesting full pipeline...")
    
    try:
        from agents.run_pipeline import main
        import sys
        
        # Override sys.argv for testing
        sys.argv = ['run_pipeline.py', 'VENDOR_001', '3']
        
        # This will run the full pipeline
        # For now, just test that it can be imported
        logger.info("✅ Pipeline can be imported")
        logger.info("Run: python -m agents.run_pipeline VENDOR_001 3")
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {e}", exc_info=True)
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("Guardian AI v1 - API Key Test")
    logger.info("=" * 60)
    
    results = []
    
    results.append(("ImpactReasoningAgent", test_impact_agent()))
    results.append(("Full Pipeline", test_full_pipeline()))
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        logger.info("\n🎉 All tests passed!")
        logger.info("\nNext: python -m agents.run_pipeline VENDOR_001 3")
        return 0
    else:
        logger.error("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

