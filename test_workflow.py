import requests
import time
import json
import sys

API_URL = "http://localhost:8000"

def run_test():
    print("🚀 Starting End-to-End Test...")
    
    # 1. Check API Health
    try:
        requests.get(f"{API_URL}/docs")
        print("✅ API Gateway is reachable.")
    except Exception as e:
        print(f"❌ API Gateway not reachable: {e}")
        sys.exit(1)

    # 2. Create Workflow
    payload = {
        "name": "Self Healing Test",
        "tasks": [
            {
                "name": "Task 1 (Normal)",
                "task_type": "HTTP_REQUEST",
                "payload": {"simulate_failure": False},
                "next_task": "Task 2 (Fail)",
                "max_retries": 3
            },
            {
                "name": "Task 2 (Fail)",
                "task_type": "COMPUTE",
                "payload": {"simulate_failure": True},
                "next_task": "Task 3 (Should Run After Recovery?)", 
                # Note: IF failure is simulated in code, retry engine retries it. 
                # If it keeps failing, it eventually fails workflow. 
                # If it succeeds on retry (logic dep), it continues.
                # My worker code simulates failure EVERY time if 'simulate_failure' is True.
                # So it will fail 3 times and stop.
                "max_retries": 3
            }
        ]
    }
    
    print(f"\nCreating Workflow: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{API_URL}/workflows", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Failed to create workflow: {response.text}")
        sys.exit(1)
        
    workflow = response.json()
    wf_id = workflow["id"]
    print(f"✅ Workflow Created: {wf_id}")
    
    # 3. Poll Status
    print("\nSimulating execution/failure/retry loop (Polling every 2s)...")
    for i in range(20):
        time.sleep(2)
        res = requests.get(f"{API_URL}/workflows/{wf_id}")
        data = res.json()
        status = data["status"]
        
        # Print valid tasks status
        task_statuses = [f"{t['name']}: {t['status']} (Retries: {t['retry_count']})" for t in data["tasks"]]
        print(f"[{i*2}s] Workflow: {status} | Tasks: {', '.join(task_statuses)}")
        
        # Check if tasks failed and were retried
        failed_tasks = [t for t in data["tasks"] if t["status"] == "FAILED"]
        retried_tasks = [t for t in data["tasks"] if t["retry_count"] > 0]
        
        if retried_tasks:
            print("   ⚠️ Retry detected! Self-healing in action.")

        if status in ["COMPLETED", "FAILED"]:
            break
            
    print("\n✅ Test Completed.")

if __name__ == "__main__":
    run_test()
