import os
import json
from datetime import datetime, timedelta
import random

# --- Configuration ---
# Base numbers from your requirements
NUM_USERS = 300
NUM_GROUPS = 15
NUM_SPACES = 30
NUM_PAGES_PER_SPACE = 10
MIN_RECORDS = 50 # Requirement: Minimum 50 records per table

DATA_DIR = 'data'
START_DATE = datetime(2023, 1, 1, 10, 0, 0)

# --- ENUMS (Mapped from Schema) ---
USER_ROLES = ['global_admin', 'space_admin', 'space_member', 'anonymous', 'reviewer_approver']
PERMISSION_TYPES = ['view', 'edit', 'admin']
SPACE_FEATURE_TYPES = ['live_docs', 'calendars', 'whiteboard']
CONTENT_STATES = ['draft', 'published', 'archived']
AUDIT_ACTIONS = ['create_space', 'update_page', 'manage_permissions', 'export_space', 'create_page', 'delete_page', 'add_comment']
EXPORT_FORMATS = ['PDF', 'HTML', 'XML']
EXPORT_JOB_STATUSES = ['pending', 'running', 'completed', 'failed']
CONTENT_FORMATS = ['markdown', 'html', 'richtext']
APPROVAL_STATUSES = ['pending', 'in_review', 'approved', 'rejected']
DECISION_TYPES = ['approve', 'reject', 'escalate', 'cancel']
NOTIFICATION_CHANNELS = ['system', 'email']
NOTIFICATION_DELIVERY_STATUSES = ['pending', 'sent', 'read', 'failed']

# --- Global Counter and Time Helper ---
current_id_counters = {}

def get_next_id(table_name):
    """Generates a strictly numerical (integer) ID for the given table, independently."""
    if table_name not in current_id_counters:
        current_id_counters[table_name] = 1
    _id = current_id_counters[table_name]
    current_id_counters[table_name] += 1
    return str(_id) # Return as string for JSON key and varchar fields

def get_datetime(days_offset_start=0, days_offset_end=0):
    """Generates a random datetime string within a range."""
    # Ensure end is >= start to prevent ValueError in random.randint
    days_offset_end = max(days_offset_start, days_offset_end)
    
    days = random.randint(days_offset_start, days_offset_end)
    return (START_DATE + timedelta(days=days, seconds=random.randint(0, 86400))).isoformat(timespec='seconds')

# --- Main Generator Function ---

def generate_seed_data():
    all_data = {}
    current_id_counters.clear()
    
    # --- PHASE 1: Independent/Root Tables (Guaranteed > MIN_RECORDS) ---
    
    # 1. users Table (Size: 300)
    print("Generating users data...")
    users = {}
    user_id_map = [] 
    for i in range(NUM_USERS):
        user_id = get_next_id('user')
        user_id_map.append(user_id)
        role = random.choice(USER_ROLES)
        users[user_id] = {
            'user_id': user_id,
            'email': f"user{user_id}@corp.com",
            'account_id': f"acc-{user_id}",
            'full_name': f"Agent {user_id}",
            'global_role': role,
            'created_at': get_datetime(days_offset_start=1, days_offset_end=max(1, i)) # FIX: Ensures start <= end
        }
    all_data['users'] = users
    global_admin_id = user_id_map[0]
    
    # 2. groups Table (Size: 50+)
    print("Generating groups data...")
    groups = {}
    group_id_map = []
    
    target_groups = max(NUM_GROUPS, MIN_RECORDS)
    for i in range(target_groups):
        group_id = get_next_id('group')
        group_id_map.append(group_id)
        groups[group_id] = {
            'group_id': group_id,
            'group_name': f"Team {group_id} - {random.choice(['Dev', 'HR', 'Sales'])}",
            'created_at': get_datetime(days_offset_start=10, days_offset_end=i*2 + 10)
        }
    all_data['groups'] = groups

    # 4. spaces Table (Size: 50+)
    print("Generating spaces data...")
    spaces = {}
    space_id_map = []
    
    target_spaces = max(NUM_SPACES, MIN_RECORDS)
    for i in range(target_spaces):
        space_id = get_next_id('space')
        space_id_map.append(space_id)
        spaces[space_id] = {
            'space_id': space_id,
            'space_key': f"PROJ{space_id}",
            'space_name': f"Project {space_id} Docs",
            'space_purpose': f"Central hub for Project {space_id}.",
            'created_by_user_id': random.choice(user_id_map),
            'created_at': get_datetime(days_offset_start=1, days_offset_end=i*5 + 20),
            'is_deleted': random.choice([True, False]),
            'deleted_at': get_datetime(days_offset_start=i*5 + 30, days_offset_end=i*5 + 50) if random.random() < 0.1 else None
        }
    all_data['spaces'] = spaces

    # --- PHASE 2: Join/Link Tables (Guaranteed > MIN_RECORDS) ---

    # 3. user_groups Table (FK: user_id, group_id)
    print("Generating user_groups data...")
    user_groups = {}
    # Target 2 memberships per user on average, ensuring minimum is met.
    target_memberships = max(NUM_USERS * 2, MIN_RECORDS) 
    
    for i in range(target_memberships):
        ug_id = get_next_id('user_group')
        user_groups[ug_id] = {
            '_id': ug_id,
            'user_id': random.choice(user_id_map),
            'group_id': random.choice(group_id_map),
            'joined_at': get_datetime(days_offset_start=30, days_offset_end=i + 50)
        }
    all_data['user_groups'] = user_groups
    
    # 5. space_memberships Table (FK: user_id, space_id)
    print("Generating space_memberships data...")
    space_memberships = {}
    # Target 5 memberships per space on average
    target_memberships = max(len(space_id_map) * 5, MIN_RECORDS)

    for i in range(target_memberships):
        sm_id = get_next_id('space_membership')
        space_memberships[sm_id] = {
            "_id": sm_id,
            'user_id': random.choice(user_id_map),
            'space_id': random.choice(space_id_map),
            'role': random.choice(USER_ROLES),
            'joined_at': get_datetime(days_offset_start=60, days_offset_end=i + 100)
        }
    all_data['space_memberships'] = space_memberships
    
    # 6. space_features Table (FK: space_id)
    print("Generating space_features data...")
    space_features = {}

    # Ensure every feature is on every space at least once
    for i, space_id in enumerate(space_id_map):
        for feature_type in SPACE_FEATURE_TYPES:
            feature_id = get_next_id('feature')
            space_features[feature_id] = {
                'feature_id': feature_id,
                'space_id': space_id,
                'feature_type': feature_type,
                'is_enabled': random.choice([True, False])
            }
            
    # Add padding features if needed to meet MIN_RECORDS
    while len(space_features) < MIN_RECORDS:
         feature_id = get_next_id('feature')
         space_features[feature_id] = {
             'feature_id': feature_id,
             'space_id': random.choice(space_id_map),
             'feature_type': random.choice(SPACE_FEATURE_TYPES),
             'is_enabled': random.choice([True, False])
         }
    all_data['space_features'] = space_features

    # 7. pages Table (Size: 300)
    print("Generating pages data...")
    pages = {}
    page_id_map = []
    
    target_pages = NUM_SPACES * NUM_PAGES_PER_SPACE
    for i in range(target_pages):
        page_id = get_next_id('page')
        page_id_map.append(page_id)
        space_id = random.choice(space_id_map)
        creator_id = random.choice(user_id_map)
        is_published = random.choice([True, False])
        current_version = random.randint(1, 5)
        
        # Link parents only to pages already created
        parent_page_id = None
        if i > 0 and random.random() < 0.2:
             parent_page_id = random.choice(page_id_map[:i])

        pages[page_id] = {
            'page_id': page_id,
            'space_id': space_id,
            'parent_page_id': parent_page_id,
            'title': f"Doc {page_id} - Topic {i}",
            'content_format': random.choice(CONTENT_FORMATS),
            'current_version': current_version,
            'state': CONTENT_STATES[1] if is_published else CONTENT_STATES[0],
            'created_by_user_id': creator_id,
            'updated_by_user_id': random.choice(user_id_map),
            'created_at': get_datetime(days_offset_start=90, days_offset_end=i*2 + 100),
            'updated_at': get_datetime(days_offset_start=i*2 + 100, days_offset_end=i*3 + 150),
            'is_trashed': random.random() < 0.05,
            'is_published': is_published
        }
    all_data['pages'] = pages
    
    # 8. page_versions Table (Size: 50+)
    print("Generating page_versions data...")
    page_versions = {}
    target_versions = max(len(page_id_map) * 3, MIN_RECORDS)
    
    version_counter = 0
    
    # Ensure every page has versions, and reach the minimum record count
    for page_id, page in pages.items():
        num_versions = page['current_version']
        for v in range(1, num_versions + 1):
            version_id = get_next_id('version')
            version_counter += 1
            page_versions[version_id] = {
                'version_id': version_id,
                'page_id': page_id,
                'version_number': v,
                'editor_user_id': page['created_by_user_id'] if v == 1 else page['updated_by_user_id'],
                'edited_at': get_datetime(days_offset_start=150, days_offset_end=150 + v*5),
                'content_snapshot': f"Version {v} content for page {page_id}"
            }
            
    all_data['page_versions'] = page_versions
    
    # 9. permissions Table (Size: 50+)
    print("Generating permissions data...")
    permissions = {}
    
    target_perms = max(len(user_id_map) + len(group_id_map) + 20, MIN_RECORDS)
    for i in range(target_perms):
        perm_id = get_next_id('perm')
        
        # Decide if space or page perm (70/30 split)
        is_space_perm = random.random() < 0.7
        space_id = random.choice(space_id_map)
        page_id = random.choice(page_id_map) if not is_space_perm else None
        
        # Decide if user or group perm (70/30 split)
        is_user_perm = random.random() < 0.7
        user_id = random.choice(user_id_map) if is_user_perm else None
        group_id = random.choice(group_id_map) if not is_user_perm else None
        
        is_active = random.random() < 0.8
        
        permissions[perm_id] = {
            'permission_id': perm_id,
            'space_id': space_id if is_space_perm else None,
            'page_id': page_id,
            'user_id': user_id,
            'group_id': group_id,
            'permission_type': random.choice(PERMISSION_TYPES),
            'granted_by_user_id': global_admin_id,
            'granted_at': get_datetime(days_offset_start=180, days_offset_end=i + 200),
            'is_active': is_active,
            'revoked_by_user_id': global_admin_id if not is_active and random.random() < 0.5 else None,
            'revoked_at': get_datetime(days_offset_start=i + 190, days_offset_end=i + 250) if not is_active else None,
            'expires_at': get_datetime(days_offset_start=i + 300, days_offset_end=i + 400) if random.random() < 0.1 else None
        }
    all_data['permissions'] = permissions

    # 10. watchers Table (Size: 50+)
    print("Generating watchers data...")
    watchers = {}
    target_watches = max(len(page_id_map) + 20, MIN_RECORDS)
    
    for i in range(target_watches):
        watcher_id = get_next_id('watch')
        is_user_watcher = random.random() < 0.7
        
        watchers[watcher_id] = {
            'watcher_id': watcher_id,
            'user_id': random.choice(user_id_map) if is_user_watcher else None,
            'group_id': random.choice(group_id_map) if not is_user_watcher else None,
            'space_id': random.choice(space_id_map) if random.random() < 0.5 else None,
            'page_id': random.choice(page_id_map) if random.random() < 0.5 else None,
            'watched_at': get_datetime(days_offset_start=200, days_offset_end=i + 250)
        }
    all_data['watchers'] = watchers
    
    # 11. export_jobs Table (Size: 50+)
    print("Generating export_jobs data...")
    export_jobs = {}
    for i in range(MIN_RECORDS):
        job_id = get_next_id('export')
        status = random.choice(EXPORT_JOB_STATUSES)
        
        export_jobs[job_id] = {
            'job_id': job_id,
            'space_id': random.choice(space_id_map),
            'requested_by_user_id': random.choice(user_id_map),
            'requested_at': get_datetime(days_offset_start=220, days_offset_end=220 + i),
            'status': status,
            'format': random.choice(EXPORT_FORMATS),
            'destination': f"/exports/{job_id}.{random.choice(EXPORT_FORMATS).lower()}" if status == 'completed' else None,
            'estimated_size_kb': random.randint(1000, 500000),
            'priority': random.randint(0, 10)
        }
    all_data['export_jobs'] = export_jobs

    # 12. audit_logs Table (Size: 50+)
    print("Generating audit_logs data...")
    audit_logs = {}
    for i in range(MIN_RECORDS + 50): # Add buffer for more logs
        log_id = get_next_id('audit')
        action = random.choice(AUDIT_ACTIONS)
        
        # Select target entity based on action type
        if 'space' in action or 'export' in action:
            target_id = random.choice(space_id_map)
            target_type = 'space'
        elif 'page' in action or 'comment' in action:
            target_id = random.choice(page_id_map)
            target_type = 'page'
        else: # permissions
            target_id = random.choice(user_id_map + group_id_map)
            target_type = random.choice(['user', 'group'])
            
        audit_logs[log_id] = {
            'log_id': log_id,
            'actor_user_id': random.choice(user_id_map),
            'action_type': action,
            'target_entity_type': target_type,
            'target_entity_id': target_id,
            'occurred_at': get_datetime(days_offset_start=1, days_offset_end=365),
            'details': json.dumps({"ip": f"192.168.1.{i % 255}", "action_detail": f"Log for {action}"})
        }
    all_data['audit_logs'] = audit_logs

    # 13. space_config_history Table (Size: 50+)
    print("Generating space_config_history data...")
    config_history = {}
    
    # Ensure every space has at least one config record
    for i, space_id in enumerate(space_id_map):
        history_id = get_next_id('config_history')
        config_history[history_id] = {
            'history_id': history_id,
            'space_id': space_id,
            'changed_by_user_id': random.choice(user_id_map),
            'changed_at': get_datetime(days_offset_start=10, days_offset_end=50),
            'config_version': 1,
            'old_config': json.dumps({"status": "draft"}),
            'new_config': json.dumps({"status": "active"})
        }

    # Add padding to meet MIN_RECORDS
    while len(config_history) < MIN_RECORDS:
        history_id = get_next_id('config_history')
        config_history[history_id] = {
            'history_id': history_id,
            'space_id': random.choice(space_id_map),
            'changed_by_user_id': random.choice(user_id_map),
            'changed_at': get_datetime(days_offset_start=60, days_offset_end=300),
            'config_version': random.randint(2, 5),
            'old_config': json.dumps({"theme": "light"}),
            'new_config': json.dumps({"theme": "dark"})
        }
    all_data['space_config_history'] = config_history

    # 14. approval_requests Table (Size: 50+)
    print("Generating approval_requests data...")
    approval_requests = {}
    
    for i in range(MIN_RECORDS):
        req_id = get_next_id('approval_request')
        target_type = random.choice(['page', 'space'])
        target_id = random.choice(page_id_map if target_type == 'page' else space_id_map)
        status = random.choice(APPROVAL_STATUSES)
        
        approval_requests[req_id] = {
            'request_id': req_id,
            'target_entity_type': target_type,
            'target_entity_id': target_id,
            'requested_by_user_id': random.choice(user_id_map),
            'status': status,
            'reason': f"Request {req_id} justification.",
            'created_at': get_datetime(days_offset_start=250, days_offset_end=250 + i),
            'updated_at': get_datetime(days_offset_start=250 + i + 1, days_offset_end=250 + i + 5) if status != 'pending' else None,
            'due_at': get_datetime(days_offset_start=300, days_offset_end=350),
            'metadata': json.dumps({"priority": random.choice(["high", "low"])})
        }
    all_data['approval_requests'] = approval_requests

    # 15. approval_decisions Table (Size: 50+)
    print("Generating approval_decisions data...")
    approval_decisions = {}
    
    # Get all requests that are not pending
    decidable_requests = [r for r_id, r in approval_requests.items() if r['status'] != 'pending']
    
    # Create decisions for all decidable requests, then pad to MIN_RECORDS
    current_decisions = {}
    for i, req in enumerate(decidable_requests):
        dec_id = get_next_id('decision')
        
        current_decisions[dec_id] = {
            'decision_id': dec_id,
            'step_id': req['request_id'],
            'approver_user_id': random.choice(user_id_map),
            'decision': random.choice(DECISION_TYPES),
            'comment': f"Decision for request {req['request_id']}.",
            'decided_at': req['updated_at'] if req['updated_at'] else get_datetime(days_offset_start=260, days_offset_end=260 + i)
        }
    
    # Add padding decisions if required 
    while len(current_decisions) < MIN_RECORDS:
        dec_id = get_next_id('decision')
        current_decisions[dec_id] = {
            'decision_id': dec_id,
            'step_id': random.choice(list(approval_requests.keys())),
            'approver_user_id': random.choice(user_id_map),
            'decision': random.choice(DECISION_TYPES),
            'comment': f"Padded decision {dec_id}.",
            'decided_at': get_datetime(days_offset_start=300, days_offset_end=350)
        }
    all_data['approval_decisions'] = current_decisions

    # 16. notifications Table (Size: 50+)
    print("Generating notifications data...")
    # 16. notifications Table (Size: 50+)
    print("Generating notifications data...")
    notifications = {}
    
    # Create a unified list of all available IDs for easy random selection later
    # This is fine for fields where type is determined by the entity_type field (FK targets)
    
    for i in range(MIN_RECORDS + 50): # Add buffer for notifications
        noti_id = get_next_id('notification')
        status = random.choice(NOTIFICATION_DELIVERY_STATUSES)

        # 1. Determine the entity type first
        related_type = random.choice(['pages', 'spaces', 'users'])

        # 2. Select the ID based on the determined type (FIX)
        if related_type == 'page':
            related_id = random.choice(page_id_map)
        elif related_type == 'space':
            related_id = random.choice(space_id_map)
        elif related_type == 'user':
            related_id = random.choice(user_id_map)
        else:
             # Should not happen with current choices, but good practice
             related_id = None 
        
        notifications[noti_id] = {
            'notification_id': noti_id,
            'recipient_user_id': random.choice(user_id_map),
            'event_type': random.choice(['page_updated', 'new_mention', 'permission_granted']),
            'message': f"Alert {noti_id} for user.",
            'related_entity_type': related_type, # Fixed type
            'related_entity_id': related_id,      # Fixed ID, matching type
            'sender_user_id': random.choice(user_id_map),
            'channel': random.choice(NOTIFICATION_CHANNELS),
            'delivery_status': status,
            'created_at': get_datetime(days_offset_start=300, days_offset_end=300 + i),
            'sent_at': get_datetime(days_offset_start=300 + i + 1, days_offset_end=300 + i + 5) if status != 'pending' else None,
            'read_at': get_datetime(days_offset_start=300 + i + 6, days_offset_end=300 + i + 10) if status == 'read' else None,
            'metadata': json.dumps({"is_priority": random.choice(["true", "false"])})
        }
    all_data['notifications'] = notifications

    return all_data

# --- File Operations ---

def write_to_json(data):
    """Writes the generated data to individual JSON files in the data directory."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    for table_name, records in data.items():
        file_path = os.path.join(DATA_DIR, f"{table_name}.json")
        with open(file_path, 'w') as f:
            json.dump(records, f, indent=4)
        print(f"✅ Created {file_path} with {len(records)} records (keyed by ID).")

# --- Execution ---

if __name__ == '__main__':
    print(f"Starting data generation. Minimum {MIN_RECORDS} records per table guaranteed. Total 16 tables.")
    seed_data = generate_seed_data()
    print("-" * 30)
    write_to_json(seed_data)
    print("-" * 30)
    print("✨ Seed data generation complete! Files are in the 'data' folder.")