#!/usr/bin/env python3
"""
Test script for Vertex AI deployment
Tests the deployed Guardian AI v2 model on Vertex AI
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform.gapic.schema import predict
except ImportError:
    print("Error: google-cloud-aiplatform not installed")
    print("Install it with: pip install google-cloud-aiplatform")
    sys.exit(1)


def test_prediction(endpoint_id: str, project_id: str, location: str, vendor_id: str = "VENDOR_001", max_depth: int = 2):
    """Test prediction on Vertex AI endpoint"""
    
    print(f"Testing Vertex AI endpoint: {endpoint_id}")
    print(f"Project: {project_id}, Location: {location}")
    print(f"Input: vendor_id={vendor_id}, max_depth={max_depth}")
    print()
    
    # Initialize Vertex AI
    aiplatform.init(project=project_id, location=location)
    
    # Get endpoint
    endpoint = aiplatform.Endpoint(endpoint_id)
    
    # Prepare request
    request_data = {
        "instances": [{
            "vendor_id": vendor_id,
            "max_depth": max_depth
        }]
    }
    
    print("Sending prediction request...")
    print(f"Request: {json.dumps(request_data, indent=2)}")
    print()
    
    # Make prediction
    try:
        response = endpoint.predict(instances=request_data["instances"])
        print("=" * 70)
        print("PREDICTION RESPONSE")
        print("=" * 70)
        print(json.dumps(response.predictions[0] if response.predictions else {}, indent=2))
        print()
        
        # Check success
        if response.predictions and len(response.predictions) > 0:
            result = response.predictions[0]
            if result.get("success"):
                print("✅ Prediction successful!")
                if "simulation_results" in result:
                    sim = result["simulation_results"]
                    print(f"   - Found {len(sim.get('propagation_paths', []))} propagation paths")
                    print(f"   - Affected {sim.get('total_affected_nodes', 0)} nodes")
                if "impact_explanations" in result:
                    print(f"   - Generated {len(result['impact_explanations'])} impact explanations")
                if "mitigation_recommendations" in result:
                    print(f"   - Ranked {len(result['mitigation_recommendations'])} mitigations")
            else:
                print(f"❌ Prediction failed: {result.get('error_message', 'Unknown error')}")
        else:
            print("❌ No predictions returned")
            
    except Exception as e:
        print(f"❌ Error making prediction: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_health_check(endpoint_id: str, project_id: str, location: str):
    """Test health check endpoint"""
    print(f"Testing health check for endpoint: {endpoint_id}")
    
    # This would require custom endpoint implementation
    # For now, just check if endpoint exists
    try:
        aiplatform.init(project=project_id, location=location)
        endpoint = aiplatform.Endpoint(endpoint_id)
        print(f"✅ Endpoint exists: {endpoint.display_name}")
        return True
    except Exception as e:
        print(f"❌ Error checking endpoint: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test Guardian AI v2 Vertex AI deployment")
    parser.add_argument("--endpoint-id", required=True, help="Vertex AI endpoint ID")
    parser.add_argument("--project-id", default=None, help="GCP Project ID (default: from environment)")
    parser.add_argument("--location", default="us-central1", help="GCP Location (default: us-central1)")
    parser.add_argument("--vendor-id", default="VENDOR_001", help="Test vendor ID (default: VENDOR_001)")
    parser.add_argument("--max-depth", type=int, default=2, help="Test max depth (default: 2)")
    parser.add_argument("--health-only", action="store_true", help="Only run health check")
    
    args = parser.parse_args()
    
    # Get project ID from environment if not provided
    project_id = args.project_id or os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID is required")
        print("Set it as environment variable or use --project-id")
        sys.exit(1)
    
    if args.health_only:
        test_health_check(args.endpoint_id, project_id, args.location)
    else:
        test_prediction(
            args.endpoint_id,
            project_id,
            args.location,
            args.vendor_id,
            args.max_depth
        )


if __name__ == "__main__":
    main()


