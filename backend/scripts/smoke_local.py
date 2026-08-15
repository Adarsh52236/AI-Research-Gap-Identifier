import os
import time
import requests
import sys

BASE_URL = os.environ.get("LOCAL_BACKEND_BASE_URL", "http://localhost:8001")

def get_token():
    return os.environ.get("SMOKE_LOCAL_TOKEN", "")

def main():
    headers = {"Content-Type": "application/json"}
    token = get_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"=== Starting Local Smoke Test against {BASE_URL} ===")
    
    # 1. Health
    try:
        res = requests.get(f"{BASE_URL}/api/v1/health/", timeout=5)
        res.raise_for_status()
        print("[OK] Health check passed.")
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        sys.exit(1)

    # 2. Deep Health
    try:
        res = requests.get(f"{BASE_URL}/api/v1/health/deep", timeout=5)
        res.raise_for_status()
        data = res.json()
        print(f"[OK] Deep Health: DB={data.get('db_ok')}, Storage={data.get('supabase_storage_ok')}")
        if not data.get('db_ok') and data.get('status') == 'degraded':
            print("  Warning: DB connection might be degraded.")
    except Exception as e:
        print(f"[FAIL] Deep health failed: {e}")
        sys.exit(1)

    # 3. Start Pipeline
    payload = {
        "query": "kv cache",
        "limit": 2,
        "steps": ["search"]
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/v1/analysis/pipeline-run/?async_run=true", json=payload, headers=headers, timeout=10)
        
        if res.status_code == 401:
            print("[FAIL] 401 Unauthorized. Provide SMOKE_LOCAL_TOKEN env var to run this test if auth is enforced.")
            sys.exit(1)
            
        res.raise_for_status()
        run_data = res.json()
        run_id = run_data.get("run_id")
        if not run_id:
            print("[FAIL] No run_id returned.")
            sys.exit(1)
        print(f"[OK] Pipeline started asynchronously. Run ID: {run_id}")
    except Exception as e:
        print(f"[FAIL] Failed to start pipeline: {e}")
        sys.exit(1)

    # 4. Poll
    print("--- Polling for completion ---")
    max_duration = 60
    interval = 3
    elapsed = 0
    not_found_count = 0
    
    while elapsed < max_duration:
        try:
            res = requests.get(f"{BASE_URL}/api/v1/analysis/pipeline-run/{run_id}", headers=headers, timeout=5)
            if res.status_code == 404:
                not_found_count += 1
                if not_found_count >= 2:
                    print("[FAIL] Run ID not found (404) twice. Storage persistence failed.")
                    sys.exit(1)
            elif res.status_code == 502 or res.status_code == 500:
                print(f"[{elapsed}s] 502/500 Backend issue. Retrying...")
            else:
                res.raise_for_status()
                status_data = res.json()
                status = status_data.get("status")
                print(f"[{elapsed}s] Status: {status} (Step: {status_data.get('current_step', 'N/A')})")
                
                if status == "completed":
                    print("[SUCCESS] Local smoke test passed!")
                    sys.exit(0)
                elif status == "failed":
                    print(f"[FAIL] Pipeline failed. Errors: {status_data.get('errors')}")
                    sys.exit(1)
        except Exception as e:
             print(f"[{elapsed}s] Request error: {e}")
             
        time.sleep(interval)
        elapsed += interval

    print(f"[FAIL] Polling timed out after {max_duration} seconds.")
    sys.exit(1)

if __name__ == "__main__":
    main()
