import requests
import sys
import os
import pandas as pd

def verify_api():
    base_url = "http://localhost:8000"
    
    print(f"Checking API at {base_url}...")
    
    # 1. Check Health
    try:
        resp = requests.get(f"{base_url}/health")
        if resp.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {resp.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running?")
        print("Run: uvicorn backend.api.main:app --reload")
        return

    # 2. Check Data Loading
    print("\nVerifying Data Loading...")
    try:
        resp = requests.get(f"{base_url}/api/risk/nodes")
        data = resp.json()
        
        if data['success']:
            nodes = data['data']
            print(f"✅ Loaded {len(nodes)} nodes from API")
            
            # Verify against CSV if possible
            csv_path = os.path.join("backend", "data", "vendors.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                print(f"ℹ️  CSV contains {len(df)} rows")
                
                # Check for a known vendor from CSV
                vendor_id = df.iloc[0]['id']
                found = any(n['node_id'] == vendor_id for n in nodes)
                if found:
                    print(f"✅ Confirmed vendor {vendor_id} from CSV is present in API response")
                else:
                    print(f"❌ Vendor {vendor_id} not found in API response")
            else:
                print("⚠️  vendors.csv not found locally to compare")
        else:
            print("❌ API returned error for nodes")
            
    except Exception as e:
        print(f"❌ Failed to fetch nodes: {e}")

    # 3. Check graph export
    print("\nVerifying Graph Export...")
    try:
        resp = requests.get(f"{base_url}/api/graph/export")
        data = resp.json()
        if data['success']:
            elements = data['data']['elements']
            print(f"✅ Graph export successful: {len(elements['nodes'])} nodes, {len(elements['edges'])} edges")
        else:
            print("❌ Graph export failed")
    except Exception as e:
        print(f"❌ Failed to fetch graph: {e}")

if __name__ == "__main__":
    verify_api()
