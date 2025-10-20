import os
import json
from datetime import datetime, timedelta
import random

# --- Configuration ---
NUM_USERS = 300
NUM_GROUPS = 15
NUM_SPACES = 30
NUM_PAGES_PER_SPACE = 10
DATA_DIR = 'data'
START_DATE = datetime(2023, 1, 1, 10, 0, 0)

# --- ENUMS (Mapped from Schema) ---
USER_ROLES = ['global_admin', 'space_admin', 'space_member', 'anonymous', 'reviewer_approver']
PERMISSION_TYPES = ['view', 'edit', 'admin']
SPACE_FEATURE_TYPES = ['live_docs', 'calendars', 'whiteboard']
CONTENT_STATES = ['draft', 'published', 'archived']
AUDIT_ACTIONS = ['create_space', 'update_page', 'manage_permissions', 'export_space']
EXPORT_FORMATS = ['PDF', 'HTML']
EXPORT_JOB_STATUSES = ['pending', 'completed']
CONTENT_FORMATS = ['markdown', 'html']
APPROVAL_STATUSES = ['pending', 'approved']
DECISION_TYPES = ['approve', 'reject']
NOTIFICATION_CHANNELS = ['system', 'email']
NOTIFICATION_DELIVERY_STATUSES = ['pending', 'read']

# --- Global Counter and Time Helper ---
current_id_counters = {}

def get_next_id(table_name):
    """Generates a strictly numerical (integer) ID for the given table, independently."""
    if table_name not in current_id_counters:
        current_id_counters[table_name] = 1
    _id = current_id_counters[table_name]
    current_id_counters[table_name] += 1
    return str(_id) # Return as string for JSON key and varchar fields

def get_datetime(days_offset=0):
    """Generates a predictable datetime string with optional offset."""
    return (START_DATE + timedelta(days=days_offset)).isoformat(timespec='seconds')

# --- Main Generator Function ---

def generate_seed_data():
    all_data = {}
    current_id_counters.clear()

    # --- PHASE 1: Independent Tables (No Foreign Keys OUT) ---

    # 1. users Table (Seed: 5 users)
    print("Generating users data...")
    users = {}
    user_id_map = [] # List of generated user IDs
    initial_roles = [USER_ROLES[0], USER_ROLES[1], USER_ROLES[2], USER_ROLES[3], USER_ROLES[4]]
    
    for i in range(NUM_USERS):
        user_id = get_next_id('user')
        user_id_map.append(user_id)
        
        record = {
            'user_id': user_id,
            'email': f"user{user_id}@corp.com",
            'account_id': f"acc-{user_id}",
            'full_name': f"Agent {user_id}",
            'global_role': initial_roles[random.randint(0, len(initial_roles)-1)],
            'created_at': get_datetime(days_offset=i*5)
        }
        users[user_id] = record
    all_data['users'] = users
    global_admin_id = user_id_map[0] # User 1
    space_admin_id = user_id_map[1]  # User 2
    
    # 2. groups Table (Seed: 2 groups)
    print("Generating groups data...")
    groups = {}
    group_id_map = []
    for i in range(NUM_GROUPS):
        group_id = get_next_id('group')
        group_id_map.append(group_id)
        record = {
            'group_id': group_id,
            'group_name': f"Dev Team {group_id}",
            'created_at': get_datetime(days_offset=i*10 + 2)
        }
        groups[group_id] = record
    all_data['groups'] = groups

    # --- PHASE 2: Tables Dependent on Users/Groups ---

    # 3. user_groups Table (FK: user_id, group_id)
    print("Generating user_groups data...")
    user_groups = {}
    memberships = [
        (user_id_map[2], group_id_map[0], 25), # User 3 in Group 1
        (user_id_map[3], group_id_map[0], 27), # User 4 in Group 1
        (user_id_map[4], group_id_map[1], 29), # User 5 in Group 2
    ]
    for i, (uid, gid, offset) in enumerate(memberships):
        ug_id = get_next_id('user_group')
        user_groups[ug_id] = {
            '_id': ug_id,
            'user_id': uid,
            'group_id': gid,
            'joined_at': get_datetime(days_offset=offset)
        }
    all_data['user_groups'] = user_groups

    # 4. spaces Table (FK: created_by_user_id)
    print("Generating spaces data...")
    spaces = {}
    space_id_map = []
    for i in range(NUM_SPACES):
        space_id = get_next_id('space')
        space_id_map.append(space_id)
        record = {
            'space_id': space_id,
            'space_key': f"PROJ{space_id}",
            'space_name': f"Project {space_id} Docs",
            'space_purpose': f"Central hub for Project {space_id}.",
            'created_by_user_id': global_admin_id if i == 0 else space_admin_id,
            'created_at': get_datetime(days_offset=i*30 + 10),
            'is_deleted': False,
            'deleted_at': None
        }
        spaces[space_id] = record
    all_data['spaces'] = spaces

    # 5. space_memberships Table (FK: user_id, space_id)
    print("Generating space_memberships data...")
    space_memberships = {}
    membership_data = [
        (space_admin_id, space_id_map[0], USER_ROLES[1], 45), # User 2 is Admin of Space 1
        (user_id_map[2], space_id_map[0], USER_ROLES[2], 46), # User 3 is Member of Space 1
        (user_id_map[4], space_id_map[1], USER_ROLES[2], 50), # User 5 is Member of Space 2
    ]
    for i, (uid, sid, role, offset) in enumerate(membership_data):
        sm_id = get_next_id('space_membership')
        space_memberships[sm_id] = {
            "_id": sm_id,
            'user_id': uid,
            'space_id': sid,
            'role': role,
            'joined_at': get_datetime(days_offset=offset)
        }
    all_data['space_memberships'] = space_memberships
    
    # 6. space_features Table (FK: space_id)
    print("Generating space_features data...")
    space_features = {}
    features = [
        (space_id_map[0], SPACE_FEATURE_TYPES[0], True), # S1: Live Docs enabled
        (space_id_map[0], SPACE_FEATURE_TYPES[1], False), # S1: Calendars disabled
        (space_id_map[1], SPACE_FEATURE_TYPES[2], True), # S2: Whiteboard enabled
    ]
    for sid, feature_type, enabled in features:
        feature_id = get_next_id('feature')
        space_features[feature_id] = {
            'feature_id': feature_id,
            'space_id': sid,
            'feature_type': feature_type,
            'is_enabled': enabled
        }
    all_data['space_features'] = space_features

    # 7. pages Table (FK: space_id, created_by_user_id, updated_by_user_id)
    print("Generating pages data...")
    pages = {}
    page_id_map = []
    
    for i, space_id in enumerate(space_id_map):
        creator_id = space_admin_id if i == 0 else user_id_map[2]
        
        for j in range(NUM_PAGES_PER_SPACE):
            page_id = get_next_id('page')
            page_id_map.append(page_id)
            
            is_published = j % 2 == 0
            
            record = {
                'page_id': page_id,
                'space_id': space_id,
                'parent_page_id': page_id_map[-2] if j > 0 else None,
                'title': f"Space {space_id} Page {j+1} - {'Published' if is_published else 'Draft'}",
                'content_format': CONTENT_FORMATS[j % 2],
                'current_version': 2,
                'state': CONTENT_STATES[1] if is_published else CONTENT_STATES[0],
                'created_by_user_id': creator_id,
                'updated_by_user_id': creator_id,
                'created_at': get_datetime(days_offset=i*30 + 15 + j*2),
                'updated_at': get_datetime(days_offset=i*30 + 18 + j*2),
                'is_trashed': False,
                'is_published': is_published
            }
            pages[page_id] = record
    all_data['pages'] = pages
    
    # 8. page_versions Table (FK: page_id, editor_user_id)
    print("Generating page_versions data...")
    page_versions = {}
    for page_id, page in pages.items():
        editor_id = page['created_by_user_id']
        
        # Version 1 (Creation)
        v1_id = get_next_id('version')
        page_versions[v1_id] = {
            'version_id': v1_id,
            'page_id': page_id,
            'version_number': 1,
            'editor_user_id': editor_id,
            'edited_at': page['created_at'],
            'content_snapshot': f"V1: Created {page['title']}"
        }
        # Version 2 (Update)
        v2_id = get_next_id('version')
        page_versions[v2_id] = {
            'version_id': v2_id,
            'page_id': page_id,
            'version_number': 2,
            'editor_user_id': editor_id,
            'edited_at': page['updated_at'],
            'content_snapshot': f"V2: Updated {page['title']} with minor corrections"
        }
    all_data['page_versions'] = page_versions

    # --- PHASE 3: Tables Dependent on Content/Spaces ---

    # 9. permissions Table (FK: space_id, page_id, user_id/group_id, granted_by_user_id)
    print("Generating permissions data...")
    permissions = {}
    perms = [
        # Space 1: Group 1 has 'view' access
        (space_id_map[0], None, None, group_id_map[0], PERMISSION_TYPES[0], 100),
        # Space 2: User 4 has 'admin' access
        (space_id_map[1], None, user_id_map[3], None, PERMISSION_TYPES[2], 105),
        # Page 1: User 5 has specific 'edit' access
        (None, page_id_map[0], user_id_map[4], None, PERMISSION_TYPES[1], 110),
    ]
    for i, (sid, pid, uid, gid, ptype, offset) in enumerate(perms):
        perm_id = get_next_id('perm')
        permissions[perm_id] = {
            'permission_id': perm_id,
            'space_id': sid,
            'page_id': pid,
            'user_id': uid,
            'group_id': gid,
            'permission_type': ptype,
            'granted_by_user_id': global_admin_id,
            'granted_at': get_datetime(days_offset=offset),
            'is_active': True,
            'revoked_by_user_id': None,
            'revoked_at': None,
            'expires_at': None
        }
    all_data['permissions'] = permissions

    # 10. watchers Table (FK: user_id/group_id, space_id, page_id)
    print("Generating watchers data...")
    watchers = {}
    watches = [
        (user_id_map[2], None, space_id_map[0], None, 120), # User 3 watches Space 1
        (None, group_id_map[1], None, page_id_map[1], 125), # Group 2 watches Page 2
    ]
    for uid, gid, sid, pid, offset in watches:
        watcher_id = get_next_id('watch')
        watchers[watcher_id] = {
            'watcher_id': watcher_id,
            'user_id': uid,
            'group_id': gid,
            'space_id': sid,
            'page_id': pid,
            'watched_at': get_datetime(days_offset=offset)
        }
    all_data['watchers'] = watchers
    
    # 11. export_jobs Table (FK: space_id, requested_by_user_id)
    print("Generating export_jobs data...")
    export_jobs = {}
    for i in range(2):
        job_id = get_next_id('export')
        status = EXPORT_JOB_STATUSES[i % 2]
        export_jobs[job_id] = {
            'job_id': job_id,
            'space_id': space_id_map[i],
            'requested_by_user_id': user_id_map[i],
            'requested_at': get_datetime(days_offset=140 + i*5),
            'status': status,
            'format': EXPORT_FORMATS[i % 2],
            'destination': f"/exports/{job_id}.{EXPORT_FORMATS[i % 2].lower()}" if status == 'completed' else None,
            'estimated_size_kb': 5000 + i * 1000,
            'priority': i
        }
    all_data['export_jobs'] = export_jobs

    # 12. audit_logs Table (FK: actor_user_id)
    print("Generating audit_logs data...")
    audit_logs = {}
    
    # Log 1: User 1 creating Space 1
    log_id = get_next_id('audit')
    audit_logs[log_id] = {
        'log_id': log_id,
        'actor_user_id': global_admin_id,
        'action_type': AUDIT_ACTIONS[0],
        'target_entity_type': 'space',
        'target_entity_id': space_id_map[0],
        'occurred_at': get_datetime(days_offset=10),
        'details': json.dumps({"key": spaces[space_id_map[0]]['space_key']})
    }
    
    # Log 2: User 2 updating Page 1
    log_id = get_next_id('audit')
    audit_logs[log_id] = {
        'log_id': log_id,
        'actor_user_id': space_admin_id,
        'action_type': AUDIT_ACTIONS[1],
        'target_entity_type': 'page',
        'target_entity_id': page_id_map[0],
        'occurred_at': get_datetime(days_offset=18),
        'details': json.dumps({"title_change": "false", "version": 2})
    }
    all_data['audit_logs'] = audit_logs

    # 13. space_config_history Table (FK: space_id, changed_by_user_id)
    print("Generating space_config_history data...")
    config_history = {}
    for v in range(1, 3):
        history_id = get_next_id('config_history')
        changed_at = get_datetime(days_offset=60 + v*5)
        
        old_config = {"access": "public"}
        new_config = {"access": "private" if v % 2 == 0 else "public"}
        
        config_history[history_id] = {
            'history_id': history_id,
            'space_id': space_id_map[0],
            'changed_by_user_id': space_admin_id,
            'changed_at': changed_at,
            'config_version': v,
            'old_config': json.dumps(old_config),
            'new_config': json.dumps(new_config)
        }
    all_data['space_config_history'] = config_history

    # 14. approval_requests Table (FK: requested_by_user_id)
    print("Generating approval_requests data...")
    approval_requests = {}
    req_id = get_next_id('approval_request')
    approval_requests[req_id] = {
        'request_id': req_id,
        'target_entity_type': 'page',
        'target_entity_id': page_id_map[0],
        'requested_by_user_id': user_id_map[2], # Contributor
        'status': APPROVAL_STATUSES[1], # Approved
        'reason': "Final review before publication.",
        'created_at': get_datetime(days_offset=160),
        'updated_at': get_datetime(days_offset=165),
        'due_at': get_datetime(days_offset=180),
        'metadata': json.dumps({"level": "standard"})
    }
    all_data['approval_requests'] = approval_requests

    # 15. approval_decisions Table (FK: approver_user_id)
    print("Generating approval_decisions data...")
    approval_decisions = {}
    dec_id = get_next_id('decision')
    approval_decisions[dec_id] = {
        'decision_id': dec_id,
        'step_id': req_id, # Linking to the request ID for simplicity
        'approver_user_id': user_id_map[4], # Reviewer/Approver
        'decision': DECISION_TYPES[0],
        'comment': "Approved. Go live!",
        'decided_at': get_datetime(days_offset=165)
    }
    all_data['approval_decisions'] = approval_decisions

    # 16. notifications Table (FK: recipient_user_id, sender_user_id)
    print("Generating notifications data...")
    notifications = {}
    for i in range(2):
        noti_id = get_next_id('notification')
        notifications[noti_id] = {
            'notification_id': noti_id,
            'recipient_user_id': user_id_map[2], # Contributor
            'event_type': f"approval_complete",
            'message': f"Your request {req_id} was approved.",
            'related_entity_type': 'pages',
            'related_entity_id': page_id_map[0],
            'sender_user_id': user_id_map[4], # Approver
            'channel': NOTIFICATION_CHANNELS[0],
            'delivery_status': NOTIFICATION_DELIVERY_STATUSES[i % 2],
            'created_at': get_datetime(days_offset=170 + i),
            'sent_at': get_datetime(days_offset=171 + i),
            'read_at': get_datetime(days_offset=172 + i) if i % 2 == 1 else None,
            'metadata': json.dumps({"urgency": "medium"})
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
    print("Starting data generation with independent, numerical IDs and strict FK integrity...")
    seed_data = generate_seed_data()
    print("-" * 30)
    write_to_json(seed_data)
    print("-" * 30)
    print("✨ Seed data generation complete! Files are in the 'data' folder.")