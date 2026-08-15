import os
import time
import requests
import sys

BASE_URL = os.environ.get("CLOUD_BACKEND_BASE_URL", "https://ai-research-gap-identifier-backend.onrender.com")

def login(email, password):
    print(f"Logging in as {email}...")
    try:
        # FastAPI OAuth2PasswordRequestForm expects form data
        res = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
            "username": email,
            "password": password
        }, timeout=10)
        res.raise_for_status()
        return res.json().get("access_token")
    except Exception as e:
        print(f"[FAIL] Login failed: {e}")
        sys.exit(1)

def main():
    email = os.environ.get("CLOUD_EMAIL")
    password = os.environ.get("CLOUD_PASSWORD")
    
    headers = {"Content-Type": "application/json"}
    
    print(f"=== Starting Cloud Smoke Test against {BASE_URL} ===")

    # 1. Health
    try:
        res = requests.get(f"{BASE_URL}/api/v1/health/", timeout=10)
        res.raise_for_status()
        print("[OK] Health check passed.")
    except Exception as e:
        print(f"[FAIL] Health check failed. Is the Render instance awake? Error: {e}")
        sys.exit(1)

    # 2. Deep Health
    try:
        res = requests.get(f"{BASE_URL}/api/v1/health/deep", timeout=10)
        res.raise_for_status()
        data = res.json()
        print(f"[OK] Deep Health: DB={data.get('db_ok')}, Storage={data.get('supabase_storage_ok')}")
        if not data.get('db_ok'):
            print("  [WARN] DB connection degraded on cloud.")
    except Exception as e:
        print(f"[FAIL] Deep health failed: {e}")
        sys.exit(1)

    # 3. Login
    if email and password:
        token = login(email, password)
        headers["Authorization"] = f"Bearer {token}"
        print("[OK] Logged in successfully.")
    else:
        print("[INFO] CLOUD_EMAIL or CLOUD_PASSWORD not provided. Proceeding without auth (will fail if endpoint is protected).")

    # 4. Start Pipeline
    payload = {
        "query": "graph neural networks",
        "limit": 2,
        "steps": ["search"]
    }
    
    print(f"Initiating pipeline with payload: {payload}")
    try:
        res = requests.post(f"{BASE_URL}/api/v1/analysis/pipeline-run/?async_run=true", json=payload, headers=headers, timeout=15)
        
        if res.status_code == 401:
            print("[FAIL] 401 Unauthorized. Set CLOUD_EMAIL and CLOUD_PASSWORD env vars.")
            sys.exit(1)
            
        res.raise_for_status()
        run_data = res.json()
        run_id = run_data.get("run_id")
        if not run_id:
            print("[FAIL] No run_id returned.")
            sys.exit(1)
        print(f"[OK] Pipeline started. Run ID: {run_id}")
    except Exception as e:
        print(f"[FAIL] Failed to start pipeline: {e}")
        sys.exit(1)

    # 5. Poll with exponential backoff
    print("--- Polling for completion ---")
    max_duration = 120
    elapsed = 0
    not_found_count = 0
    consecutive_502 = 0
    poll_interval = 3
    
    while elapsed < max_duration:
        try:
            res = requests.get(f"{BASE_URL}/api/v1/analysis/pipeline-run/{run_id}", headers=headers, timeout=10)
            status_code = res.status_code
            print(f"[{elapsed}s] Poll Response: {status_code}")
            
            if status_code == 404:
                not_found_count += 1
                if not_found_count >= 2:
                    print("[FAIL] Run ID not found (404) twice.")
                    print("--> RECOMMENDATION: Ensure DBRunStore is used in production (verify DATABASE_URL and DB_ENABLED). Local disk is wiped on Render restarts.")
                    sys.exit(1)
            elif status_code in [502, 503, 504]:
                consecutive_502 += 1
                if consecutive_502 > 3:
                    print(f"[WARN] {consecutive_502} consecutive {status_code} errors.")
                    print("--> RECOMMENDATION: Check Render logs. Instance might be crashing or timing out. Ensure pipeline runs in background (async_run=true).")
            elif status_code == 200:
                consecutive_502 = 0
                not_found_count = 0
                status_data = res.json()
                status = status_data.get("status")
                print(f"  -> Status: {status} (Step: {status_data.get('current_step', 'N/A')})")
                
                if status == "completed":
                    print("[SUCCESS] Cloud smoke test passed run completion!")
                    
                    # 6. Fetch Report (Optional, just to ensure endpoint works if applicable)
                    print("Attempting to fetch report...")
                    try:
                        rep_res = requests.get(f"{BASE_URL}/api/v1/analysis/pipeline-run/{run_id}/report", headers=headers, timeout=10)
                        rep_res.raise_for_status()
                        print("[SUCCESS] Report fetched successfully.")
                    except Exception as rep_e:
                        print(f"[WARN] Failed to fetch report (this might be expected if 'report' step was skipped): {rep_e}")
                    
                    sys.exit(0)
                elif status == "failed":
                    print(f"[FAIL] Pipeline failed on backend. Errors: {status_data.get('errors')}")
                    sys.exit(1)
            else:
                print(f"[WARN] Unexpected status code: {status_code}")
                
        except requests.exceptions.RequestException as e:
             print(f"[{elapsed}s] Request exception: {e}")
             
        # Backoff logic
        time.sleep(poll_interval)
        elapsed += poll_interval
        poll_interval = min(poll_interval * 1.5, 12)

    print(f"[FAIL] Polling timed out after {max_duration} seconds.")
    print("--> RECOMMENDATION: Check if backend is getting stuck or crashed without updating run status.")
    sys.exit(1)

if __name__ == "__main__":
    main()
