#!/usr/bin/env python3
"""
Vertex AI Entry Point for Guardian AI v2
HTTP server for Vertex AI custom container predictions
"""

import os
import json
import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import Guardian AI components
try:
    from agents.registry import get_registry
    from agents.orchestrator.schema import OrchestratorInput, OrchestratorOutput
except ImportError as e:
    logger.error(f"Failed to import Guardian AI components: {e}")
    sys.exit(1)

# Import HTTP server
try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    try:
        from fastapi import FastAPI, Request
        from fastapi.responses import JSONResponse
        import uvicorn
        FASTAPI_AVAILABLE = True
        FLASK_AVAILABLE = False
    except ImportError:
        logger.error("Neither Flask nor FastAPI available. Install one: pip install flask or pip install fastapi uvicorn")
        sys.exit(1)


def validate_environment():
    """Validate that required environment variables are set"""
    required_vars = []
    optional_vars = ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GCP_PROJECT_ID"]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.warning(f"Missing optional environment variables: {missing}")
    
    # Check for Google Cloud credentials
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        logger.info("GOOGLE_APPLICATION_CREDENTIALS not set, using Application Default Credentials")
    
    logger.info("Environment validation complete")


def preprocess_request(request: Dict[str, Any]) -> OrchestratorInput:
    """
    Preprocess Vertex AI prediction request into OrchestratorInput.
    
    Vertex AI sends requests in format:
    {
        "instances": [
            {
                "vendor_id": "VENDOR_001",
                "max_depth": 3,
                "graph_metadata": {...}
            }
        ]
    }
    """
    try:
        # Handle Vertex AI request format
        if "instances" in request:
            if not request["instances"] or len(request["instances"]) == 0:
                raise ValueError("No instances provided in request")
            instance = request["instances"][0]
        else:
            # Direct format (for testing)
            instance = request
        
        # Extract and validate fields
        vendor_id = instance.get("vendor_id")
        if not vendor_id:
            raise ValueError("vendor_id is required")
        
        max_depth = instance.get("max_depth", 3)
        if not isinstance(max_depth, int) or max_depth < 1:
            max_depth = 3
            logger.warning(f"Invalid max_depth, using default: 3")
        
        graph_metadata = instance.get("graph_metadata")
        
        return OrchestratorInput(
            vendor_id=str(vendor_id),
            max_depth=max_depth,
            graph_metadata=graph_metadata
        )
    
    except Exception as e:
        logger.error(f"Failed to preprocess request: {e}")
        raise


def postprocess_response(output: OrchestratorOutput) -> Dict[str, Any]:
    """
    Postprocess OrchestratorOutput into Vertex AI prediction response format.
    
    Vertex AI expects:
    {
        "predictions": [
            {
                "success": true,
                "results": {...}
            }
        ]
    }
    """
    try:
        response_data = {
            "success": output.success,
            "execution_trace": [
                {
                    "agent_name": trace.agent_name,
                    "input_summary": trace.input_summary,
                    "output_summary": trace.output_summary,
                    "execution_time_ms": trace.execution_time_ms
                }
                for trace in output.execution_trace
            ] if output.execution_trace else []
        }
        
        if output.success:
            response_data["simulation_results"] = output.simulation_results
            response_data["impact_explanations"] = output.impact_explanations
            response_data["mitigation_recommendations"] = output.mitigation_recommendations
        else:
            response_data["error_message"] = output.error_message
            # Include partial results if available
            if output.simulation_results:
                response_data["simulation_results"] = output.simulation_results
            if output.impact_explanations:
                response_data["impact_explanations"] = output.impact_explanations
        
        return {
            "predictions": [response_data]
        }
    
    except Exception as e:
        logger.error(f"Failed to postprocess response: {e}")
        return {
            "predictions": [{
                "success": False,
                "error_message": f"Response processing failed: {str(e)}"
            }]
        }


def predict(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main prediction function called by Vertex AI.
    
    Args:
        request: Vertex AI prediction request
        
    Returns:
        Vertex AI prediction response
    """
    try:
        logger.info("Received prediction request")
        
        # Preprocess request
        input_data = preprocess_request(request)
        logger.info(f"Processing request: vendor_id={input_data.vendor_id}, max_depth={input_data.max_depth}")
        
        # Get orchestrator agent
        registry = get_registry()
        orchestrator = registry.get_agent("OrchestratorAgent")
        
        # Run pipeline
        output = orchestrator.run(input_data)
        logger.info(f"Pipeline completed: success={output.success}")
        
        # Postprocess response
        response = postprocess_response(output)
        return response
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        return {
            "predictions": [{
                "success": False,
                "error_message": str(e),
                "execution_trace": []
            }]
        }


def health_check() -> Dict[str, Any]:
    """Health check endpoint for Vertex AI"""
    try:
        registry = get_registry()
        agents = registry.list_agents()
        return {
            "status": "healthy",
            "agents_registered": len(agents),
            "agents": agents
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Initialize registry globally
_registry = None

def get_or_create_registry():
    """Get or create the agent registry"""
    global _registry
    if _registry is None:
        logger.info("Initializing Guardian AI v2 registry")
        _registry = get_registry()
        logger.info(f"Registry initialized with {len(_registry.list_agents())} agents")
    return _registry


# HTTP Server Setup
if FLASK_AVAILABLE:
    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def flask_health():
        """Health check endpoint"""
        result = health_check()
        return jsonify(result), 200 if result.get("status") == "healthy" else 503
    
    @app.route('/predict', methods=['POST'])
    def flask_predict():
        """Prediction endpoint"""
        try:
            request_data = request.get_json()
            if not request_data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            result = predict(request_data)
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Prediction endpoint error: {e}", exc_info=True)
            return jsonify({
                "predictions": [{
                    "success": False,
                    "error_message": str(e)
                }]
            }), 500
    
    @app.route('/', methods=['GET'])
    def flask_root():
        """Root endpoint"""
        return jsonify({
            "service": "Guardian AI v2",
            "status": "running",
            "endpoints": ["/health", "/predict"]
        }), 200

else:
    # FastAPI setup
    app = FastAPI(title="Guardian AI v2", version="2.0.0")
    
    @app.get('/health')
    async def fastapi_health():
        """Health check endpoint"""
        result = health_check()
        status_code = 200 if result.get("status") == "healthy" else 503
        return JSONResponse(content=result, status_code=status_code)
    
    @app.post('/predict')
    async def fastapi_predict(request: Request):
        """Prediction endpoint"""
        try:
            request_data = await request.json()
            result = predict(request_data)
            return JSONResponse(content=result, status_code=200)
        except Exception as e:
            logger.error(f"Prediction endpoint error: {e}", exc_info=True)
            return JSONResponse(
                content={
                    "predictions": [{
                        "success": False,
                        "error_message": str(e)
                    }]
                },
                status_code=500
            )
    
    @app.get('/')
    async def fastapi_root():
        """Root endpoint"""
        return JSONResponse(content={
            "service": "Guardian AI v2",
            "status": "running",
            "endpoints": ["/health", "/predict"]
        }, status_code=200)


# Update predict function to use global registry
def predict_with_registry(request: Dict[str, Any]) -> Dict[str, Any]:
    """Predict using global registry"""
    try:
        logger.info("Received prediction request")
        
        # Preprocess request
        input_data = preprocess_request(request)
        logger.info(f"Processing request: vendor_id={input_data.vendor_id}, max_depth={input_data.max_depth}")
        
        # Get orchestrator agent
        registry = get_or_create_registry()
        orchestrator = registry.get_agent("OrchestratorAgent")
        
        # Run pipeline
        output = orchestrator.run(input_data)
        logger.info(f"Pipeline completed: success={output.success}")
        
        # Postprocess response
        response = postprocess_response(output)
        return response
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        return {
            "predictions": [{
                "success": False,
                "error_message": str(e),
                "execution_trace": []
            }]
        }

# Replace predict function
predict = predict_with_registry


# Main execution
if __name__ == "__main__":
    # Validate environment
    validate_environment()
    
    # Initialize registry
    get_or_create_registry()
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        logger.info("Running local test...")
        test_request = {
            "instances": [{
                "vendor_id": "VENDOR_001",
                "max_depth": 2
            }]
        }
        result = predict(test_request)
        print(json.dumps(result, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "health":
        result = health_check()
        print(json.dumps(result, indent=2))
    else:
        # Start HTTP server
        port = int(os.getenv("PORT", "3000"))
        host = os.getenv("HOST", "0.0.0.0")
        
        logger.info(f"Starting Guardian AI v2 HTTP server on {host}:{port}")
        
        if FLASK_AVAILABLE:
            app.run(host=host, port=port, debug=False)
        else:
            uvicorn.run(app, host=host, port=port, log_level="info")

