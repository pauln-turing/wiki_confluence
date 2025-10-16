import json
import os
from datetime import datetime

# --- CONFIGURATION ---
DATA_DIRECTORY = "generated_data"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
APPROVAL_REQUESTS_FILE = os.path.join(DATA_DIRECTORY, "approval_requests.json")
APPROVAL_STEPS_FILE = os.path.join(DATA_DIRECTORY, "approval_steps.json")
APPROVAL_DECISIONS_FILE = os.path.join(DATA_DIRECTORY, "approval_decisions.json")

def load_data(file_path):
    """Loads a JSON file from the specified path."""
    if not os.path.exists(file_path):
        print(f"❌ ERROR: File not found at '{file_path}'. Cannot proceed.")
        return None
    with open(file_path, 'r') as f:
        return json.load(f)

def run_verification():
    """Main function to run all verification checks."""
    print("🚀 Starting verification of approval data consistency...")
    print("-" * 50)

    # 1. Load all necessary data files
    requests = load_data(APPROVAL_REQUESTS_FILE)
    steps = load_data(APPROVAL_STEPS_FILE)
    decisions = load_data(APPROVAL_DECISIONS_FILE)

    if not all([requests, steps, decisions]):
        return # Stop if any file failed to load

    # Counters for issues
    error_count = 0
    
    # --- CHECK 1: STRUCTURAL LINKING (Parent-Child Relationships) ---
    print("🔎 Checking Rule 1: Structural Linking...")
    
    # Check if every step has a valid parent request
    for step_id, step in steps.items():
        request_id = step.get("request_id")
        if not request_id or request_id not in requests:
            print(f"  ❌ ERROR: Step '{step_id}' has an invalid or missing request_id: '{request_id}'.")
            error_count += 1

    # Check if every decision has a valid parent step
    for decision_id, decision in decisions.items():
        step_id = decision.get("step_id")
        if not step_id or step_id not in steps:
            print(f"  ❌ ERROR: Decision '{decision_id}' has an invalid or missing step_id: '{step_id}'.")
            error_count += 1
            
    if error_count == 0:
        print("  ✅ OK: All steps and decisions are correctly linked to a parent.")
        
    print("-" * 50)
    
    # --- CHECK 2: STATUS COHERENCE ---
    print("🔎 Checking Rule 2: Status Coherence...")
    initial_error_count = error_count

    # Find which steps have decisions
    steps_with_decisions = {decision['step_id'] for decision in decisions.values()}

    for step_id, step in steps.items():
        if step_id in steps_with_decisions:
            step_status = step.get("status")
            # Find the corresponding decision
            decision = next((d for d in decisions.values() if d['step_id'] == step_id), None)
            decision_type = decision.get("decision") if decision else None

            is_consistent = (
                (step_status == "approved" and decision_type == "approve") or
                (step_status == "rejected" and decision_type == "reject") or
                (step_status == "cancelled" and decision_type == "cancel")
            )
            
            if not is_consistent:
                print(f"  ❌ ERROR: Mismatch for Step '{step_id}'. Status is '{step_status}' but decision is '{decision_type}'.")
                error_count += 1

    if initial_error_count == error_count:
        print("  ✅ OK: All step statuses align with their corresponding decisions.")
        
    print("-" * 50)
    
    # --- CHECK 3: CHRONOLOGICAL ORDER ---
    print("🔎 Checking Rule 3: Chronological Order...")
    initial_error_count = error_count
    
    for decision_id, decision in decisions.items():
        step_id = decision['step_id']
        step = steps.get(step_id)
        if not step: continue # Skip if step is missing (already caught in Check 1)

        request_id = step['request_id']
        request = requests.get(request_id)
        if not request: continue # Skip if request is missing

        try:
            # Parse datetime strings into datetime objects
            request_time = datetime.strptime(request['created_at'], DATETIME_FORMAT)
            step_time = datetime.strptime(step['created_at'], DATETIME_FORMAT)
            decision_time = datetime.strptime(decision['decided_at'], DATETIME_FORMAT)

            # Check the logical time flow
            if not (request_time <= step_time <= decision_time):
                print(f"  ❌ ERROR: Chronological inconsistency found for Decision '{decision_id}':")
                print(f"    - Request created: {request_time}")
                print(f"    - Step created:    {step_time}")
                print(f"    - Decision made:   {decision_time}")
                error_count += 1
        
        except (ValueError, TypeError) as e:
            print(f"  ❌ ERROR: Could not parse datetime for Decision '{decision_id}'. Details: {e}")
            error_count += 1
            
    if initial_error_count == error_count:
        print("  ✅ OK: All timestamps follow a logical chronological order.")
        
    print("-" * 50)

    # --- FINAL SUMMARY ---
    print("\n--- Verification Summary ---")
    if error_count == 0:
        print("🎉 SUCCESS: All approval data is consistent and valid!")
    else:
        print(f"🚨 FAILED: Found {error_count} inconsistency issue(s). Please review the errors above.")

if __name__ == "__main__":
    run_verification()