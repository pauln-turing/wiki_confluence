import json
import random
import os
from datetime import datetime, timedelta
from faker import Faker

# --- CONFIGURATION ---
NUM_USERS = 50
NUM_GROUPS = 10
NUM_SPACES = 20
NUM_TEMPLATES = 15
MAX_ITEMS_PER_PARENT = 3 # Max items in "many" side of 1-to-many relationships
MIN_PAGES_PER_SPACE = 5
MAX_PAGES_PER_SPACE = 15
FREE_FORM_TEXT = "free-form-text"
FREE_FORM_JSON = {"content": "free-form-text"}
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S" # Custom datetime format
PLAUSIBLE_LABELS = [
    "meeting-notes", "bug-report", "feature-request", "q4-roadmap", "marketing-plan",
    "technical-debt", "approved", "in-review", "design-spec", "user-feedback",
    "onboarding", "performance", "security", "infra", "product-launch", "legal",
    "ux-research", "competitive-analysis", "project-alpha", "urgent", "documentation"
]

# Initialize Faker for data generation
fake = Faker()

# --- ENUM DEFINITIONS ---
USER_ROLES = [
    'global_admin', 'space_admin', 'space_member', 'anonymous',
    'reviewer_approver', 'guest', 'project_team_admin', 'content_contributor'
]
SPACE_MEMBER_ROLES = ['space_admin', 'space_member', 'guest', 'content_contributor']
PERMISSION_TYPES = ['view', 'edit', 'admin']
SPACE_FEATURE_TYPES = [
    'live_docs', 'calendars', 'whiteboard', 'databases',
    'smart_links', 'folders', 'blogs'
]
CONTENT_STATES = ['draft', 'published', 'archived']
AUDIT_ACTION_TYPES = {
    'space': ['create_space', 'update_space', 'delete_space', 'manage_permissions', 'grant_admin_rights', 'configure_settings', 'export_space', 'import_space'],
    'page': ['create_page', 'update_page', 'delete_page', 'move_page', 'rename_page', 'add_comment', 'add_label', 'restore_version', 'clone_page', 'unpublish_page', 'add_restriction', 'remove_restriction', 'archive_content'],
    'attachment': ['add_attachment', 'remove_attachment'],
    'content': ['watch_content', 'unwatch_content']
}
EXPORT_FORMATS = ['PDF', 'HTML', 'XML']
EXPORT_JOB_STATUSES = ['pending', 'running', 'completed', 'failed', 'cancelled']
CONTENT_FORMATS = ['markdown', 'html', 'richtext']
NOTIFICATION_CHANNELS = ['system', 'email']
NOTIFICATION_STATUSES = ['pending', 'sent', 'failed', 'read']
APPROVAL_STATUSES = ['pending', 'in_review', 'approved', 'rejected', 'cancelled']
DECISION_TYPES = ['approve', 'reject', 'escalate', 'cancel']
VALID_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "example.com"]
# FIX: Added a map to ensure status and decision are consistent
STATUS_TO_DECISION_MAP = {
    'approved': 'approve',
    'rejected': 'reject',
    'cancelled': 'cancel'
}


# --- HELPER FUNCTIONS ---

def generate_timestamps(start_date=None):
    """Generates a created_at and a subsequent updated_at timestamp in the custom format."""
    created_at = start_date or fake.date_time_between(start_date='-2y', end_date='now')
    # Ensure updated_at is after created_at
    time_since_creation = datetime.now() - created_at
    if time_since_creation.total_seconds() <= 0:
        updated_at = created_at + timedelta(minutes=random.randint(1, 60))
    else:
        updated_at = fake.date_time_between(start_date=created_at, end_date='now')
    return created_at.strftime(DATETIME_FORMAT), updated_at.strftime(DATETIME_FORMAT)

def generate_email(first_name, last_name):
    """Generates a realistic email from a user's name."""
    domain = random.choice(VALID_EMAIL_DOMAINS)
    return f"{first_name.lower()}.{last_name.lower()}@{domain}"

# --- MAIN GENERATION LOGIC ---

def generate_fake_data():
    """Main function to generate all data and write to JSON files."""
    print("🚀 Starting data generation for all 22 tables...")

    # Data storage dictionaries for all tables
    data = {
        "users": {}, "groups": {}, "user_groups": {}, "spaces": {}, "space_memberships": {},
        "pages": {}, "page_versions": {}, "permissions": {}, "space_features": {}, "labels": {},
        "page_labels": {}, "comments": {}, "audit_logs": {}, "templates": {}, "export_jobs": {},
        "attachments": {}, "watchers": {}, "space_config_history": {}, "notifications": {},
        "approval_requests": {}, "approval_steps": {}, "approval_decisions": {}
    }

    # ID trackers for relationships
    user_ids, group_ids, space_ids, page_ids, label_ids = [], [], [], [], []
    approval_request_ids, approval_step_ids = [], []
    all_target_entities = []

    # 1. Users
    for i in range(1, NUM_USERS + 1):
        user_id = str(i)
        first_name = fake.first_name()
        last_name = fake.last_name()
        user = {
            "user_id": user_id,
            "email": generate_email(first_name, last_name),
            "account_id": str(fake.uuid4()),
            "full_name": f"{first_name} {last_name}",
            "global_role": random.choice(USER_ROLES),
            "created_at": fake.date_time_between(start_date='-2y').strftime(DATETIME_FORMAT)
        }
        data["users"][user_id] = user
        user_ids.append(user_id)
    print(f"✔️ Generated {len(data['users'])} users.")

    # 2. Groups
    for i in range(1, NUM_GROUPS + 1):
        group_id = str(i)
        data["groups"][group_id] = {
            "group_id": group_id,
            "group_name": fake.unique.company() + " Team",
            "created_at": fake.date_time_between(start_date='-2y').strftime(DATETIME_FORMAT),
        }
        group_ids.append(group_id)
    print(f"✔️ Generated {len(data['groups'])} groups.")

    # 3. User Groups (Many-to-Many)
    user_group_pairs = set()
    for user_id in user_ids:
        num_groups = random.randint(0, MAX_ITEMS_PER_PARENT)
        if num_groups == 0: continue
        assigned_groups = random.sample(group_ids, min(num_groups, len(group_ids)))
        for group_id in assigned_groups:
            if (user_id, group_id) not in user_group_pairs:
                user_group_pairs.add((user_id, group_id))
                data["user_groups"][f"{user_id}-{group_id}"] = {
                    "user_id": user_id,
                    "group_id": group_id,
                    "joined_at": fake.date_time_between(start_date='-1y').strftime(DATETIME_FORMAT)
                }
    print(f"✔️ Generated {len(data['user_groups'])} user-group relationships.")

    # 4. Spaces
    for i in range(1, NUM_SPACES + 1):
        space_id = str(i)
        creator_id = random.choice(user_ids)
        created_at_dt = datetime.strptime(data['users'][creator_id]['created_at'], DATETIME_FORMAT)
        created_at, deleted_at = generate_timestamps(created_at_dt)
        is_deleted = random.choices([True, False], weights=[0.1, 0.9], k=1)[0]
        space = {
            "space_id": space_id,
            "space_key": fake.unique.lexify(text='????').upper(),
            "space_name": fake.bs().title(),
            "space_purpose": FREE_FORM_TEXT, # Added placeholder
            "created_by_user_id": creator_id,
            "created_at": created_at,
            "is_deleted": is_deleted,
            "deleted_at": deleted_at if is_deleted else None
        }
        data["spaces"][space_id] = space
        space_ids.append(space_id)
        all_target_entities.append(('space', space_id))
    print(f"✔️ Generated {len(data['spaces'])} spaces.")

    # 5. Space Memberships, Features, Labels (per Space)
    space_membership_pairs = set()
    label_id_counter, feature_id_counter = 1, 1
    for space_id in space_ids:
        space_creator = data['spaces'][space_id]['created_by_user_id']
        num_members = random.randint(1, int(NUM_USERS / 2))
        members = random.sample([uid for uid in user_ids if uid != space_creator], min(num_members, len(user_ids) - 1))
        all_members = members + [space_creator]
        for user_id in all_members:
             if (user_id, space_id) not in space_membership_pairs:
                space_membership_pairs.add((user_id, space_id))
                data["space_memberships"][f"{user_id}-{space_id}"] = {
                    "user_id": user_id, "space_id": space_id,
                    "role": 'space_admin' if user_id == space_creator else random.choice(SPACE_MEMBER_ROLES),
                    "joined_at": fake.date_time_between(start_date='-1y').strftime(DATETIME_FORMAT)
                }
        for feature_type in random.sample(SPACE_FEATURE_TYPES, k=random.randint(2, len(SPACE_FEATURE_TYPES))):
            feature_id = str(feature_id_counter)
            data["space_features"][feature_id] = {
                "feature_id": feature_id, "space_id": space_id, "feature_type": feature_type,
                "is_enabled": random.choices([True, False], weights=[0.9, 0.1], k=1)[0]
            }
            feature_id_counter += 1
        for _ in range(random.randint(1, MAX_ITEMS_PER_PARENT + 2)):
            label_id = str(label_id_counter)
            data["labels"][label_id] = {"label_id": label_id, "label_name": random.choice(PLAUSIBLE_LABELS), "space_id": space_id}
            label_ids.append(label_id)
            label_id_counter += 1
    print(f"✔️ Generated space memberships, features, and labels.")

    # 6. Pages & related items (Versions, Attachments, Labels, Comments)
    page_id_counter, version_id_counter, attachment_id_counter, comment_id_counter = 1, 1, 1, 1
    page_label_pairs = set()
    for space_id in space_ids:
        num_pages = random.randint(MIN_PAGES_PER_SPACE, MAX_PAGES_PER_SPACE)
        space_member_ids = [m['user_id'] for m in data['space_memberships'].values() if m['space_id'] == space_id]
        if not space_member_ids: continue

        pages_in_space = []
        for _ in range(num_pages):
            page_id = str(page_id_counter)
            creator_id, updater_id = random.choice(space_member_ids), random.choice(space_member_ids)
            created_at_dt = datetime.strptime(data['users'][creator_id]['created_at'], DATETIME_FORMAT)
            created_at, updated_at = generate_timestamps(created_at_dt)
            state = random.choice(CONTENT_STATES)
            data["pages"][page_id] = {
                "page_id": page_id, "space_id": space_id,
                "parent_page_id": random.choice(pages_in_space) if pages_in_space and random.random() > 0.5 else None,
                "title": fake.sentence(nb_words=4).replace('.', ''),
                "content_format": random.choice(CONTENT_FORMATS), "current_version": 1, "state": state,
                "created_by_user_id": creator_id, "updated_by_user_id": updater_id,
                "created_at": created_at, "updated_at": updated_at,
                "is_trashed": random.choices([True, False], weights=[0.1, 0.9], k=1)[0],
                "is_published": state == 'published'
            }
            page_ids.append(page_id); pages_in_space.append(page_id); page_id_counter += 1
            all_target_entities.append(('page', page_id))
            data["page_versions"][str(version_id_counter)] = {
                "version_id": str(version_id_counter), "page_id": page_id, "version_number": 1,
                "editor_user_id": creator_id, "edited_at": created_at,
                "content_snapshot": FREE_FORM_TEXT # Added placeholder
            }
            version_id_counter += 1
            for _ in range(random.randint(0, MAX_ITEMS_PER_PARENT)):
                attachment_id = str(attachment_id_counter)
                file_name = f"{fake.word()}.{fake.file_extension()}"
                data["attachments"][attachment_id] = {
                    "attachment_id": attachment_id, "page_id": page_id, "file_name": file_name,
                    "file_path": f"/uploads/{attachment_id}/{file_name}",
                    "file_size_bytes": random.randint(1000, 5000000),
                    "uploaded_by_user_id": random.choice(space_member_ids),
                    "uploaded_at": fake.date_time_between(start_date=datetime.strptime(created_at, DATETIME_FORMAT)).strftime(DATETIME_FORMAT)
                }
                attachment_id_counter += 1
                all_target_entities.append(('attachment', attachment_id))
            space_labels = [l['label_id'] for l in data['labels'].values() if l['space_id'] == space_id]
            if space_labels:
                for _ in range(random.randint(0, MAX_ITEMS_PER_PARENT)):
                    label_id = random.choice(space_labels)
                    if (page_id, label_id) not in page_label_pairs:
                        page_label_pairs.add((page_id, label_id))
                        data["page_labels"][f"{page_id}-{label_id}"] = {"page_id": page_id, "label_id": label_id}
            for _ in range(random.randint(0, MAX_ITEMS_PER_PARENT)):
                comment_id = str(comment_id_counter)
                author = random.choice(space_member_ids)
                created, updated = generate_timestamps(datetime.strptime(created_at, DATETIME_FORMAT))
                data["comments"][comment_id] = {
                    "comment_id": comment_id, "page_id": page_id, "author_user_id": author,
                    "comment_text": FREE_FORM_TEXT, "created_at": created, "updated_at": updated
                }
                comment_id_counter += 1
    print(f"✔️ Generated {len(data['pages'])} pages and their related items.")

    # 7. Permissions, Watchers, Export Jobs, Templates, Space Config History
    permission_id, watcher_id, job_id, template_id, history_id = 1, 1, 1, 1, 1
    for _ in range(NUM_SPACES + NUM_USERS):
        granter = random.choice(user_ids)
        granter_created_at = datetime.strptime(data['users'][granter]['created_at'], DATETIME_FORMAT)
        granted, revoked = generate_timestamps(granter_created_at)
        is_active = random.choices([True, False], weights=[0.8, 0.2], k=1)[0]
        permission = {
            "permission_id": str(permission_id), "space_id": None, "page_id": None, "user_id": None, "group_id": None,
            "permission_type": random.choice(PERMISSION_TYPES), "granted_by_user_id": granter, "granted_at": granted,
            "is_active": is_active, "revoked_by_user_id": random.choice(user_ids) if not is_active else None,
            "revoked_at": revoked if not is_active else None,
            "expires_at": (datetime.strptime(granted, DATETIME_FORMAT) + timedelta(days=90)).strftime(DATETIME_FORMAT) if random.random() > 0.8 else None,
        }
        if random.random() > 0.5: permission["user_id"] = random.choice(user_ids)
        else: permission["group_id"] = random.choice(group_ids)
        if random.random() > 0.5 and space_ids: permission["space_id"] = random.choice(space_ids)
        elif page_ids: permission["page_id"] = random.choice(page_ids)
        data["permissions"][str(permission_id)] = permission
        permission_id += 1
    for space_id in space_ids:
        if random.random() > 0.5:
            data["export_jobs"][str(job_id)] = {
                "job_id": str(job_id), "space_id": space_id, "requested_by_user_id": random.choice(user_ids),
                "requested_at": fake.date_time_between('-30d').strftime(DATETIME_FORMAT), "status": random.choice(EXPORT_JOB_STATUSES),
                "format": random.choice(EXPORT_FORMATS), "destination": f"/exports/job_{job_id}.zip",
                "estimated_size_kb": random.randint(100, 10000), "priority": random.randint(0, 5)
            }
            job_id += 1
        data["space_config_history"][str(history_id)] = {
            "history_id": str(history_id), "space_id": space_id, "changed_by_user_id": random.choice(user_ids),
            "changed_at": fake.date_time_between('-1y').strftime(DATETIME_FORMAT), "config_version": random.randint(1, 5),
            "old_config": FREE_FORM_JSON, "new_config": FREE_FORM_JSON
        }
        history_id += 1
    for _ in range(NUM_TEMPLATES):
        is_space_template = random.random() > 0.5 and space_ids
        data["templates"][str(template_id)] = {
            "template_id": str(template_id), "template_name": fake.bs().replace(' ', '-') + "-template",
            "template_content": FREE_FORM_TEXT, "is_blueprint": random.choice([True, False]),
            "space_id": random.choice(space_ids) if is_space_template else None,
            "created_by_user_id": random.choice(user_ids),
            "created_at": fake.date_time_between('-1y').strftime(DATETIME_FORMAT)
        }
        template_id += 1
    for _ in range(NUM_USERS * 2): # Create watchers
        watcher = {"watcher_id": str(watcher_id), "space_id": None, "page_id": None, "user_id": None, "group_id": None,
                   "watched_at": fake.date_time_between('-1y').strftime(DATETIME_FORMAT)}
        if random.random() > 0.5: watcher["user_id"] = random.choice(user_ids)
        else: watcher["group_id"] = random.choice(group_ids)
        if random.random() > 0.5 and space_ids: watcher["space_id"] = random.choice(space_ids)
        elif page_ids: watcher["page_id"] = random.choice(page_ids)
        data["watchers"][str(watcher_id)] = watcher
        watcher_id += 1
    print(f"✔️ Generated permissions, watchers, jobs, templates, and history.")

    # 8. Approval Cycle (Requests, Steps, Decisions)
    req_id_counter, step_id_counter, decision_id_counter = 1, 1, 1
    if page_ids:
        for _ in range(int(len(page_ids) / 4)):
            req_id, requester = str(req_id_counter), random.choice(user_ids)
            requester_created_at = datetime.strptime(data['users'][requester]['created_at'], DATETIME_FORMAT)
            created, updated = generate_timestamps(requester_created_at)
            request = {
                "request_id": req_id, "target_entity_type": 'page', "target_entity_id": random.choice(page_ids),
                "requested_by_user_id": requester, "status": random.choice(APPROVAL_STATUSES), "reason": FREE_FORM_TEXT,
                "created_at": created, "updated_at": updated,
                "due_at": (datetime.strptime(created, DATETIME_FORMAT) + timedelta(days=10)).strftime(DATETIME_FORMAT), "metadata": FREE_FORM_JSON
            }
            data["approval_requests"][req_id] = request
            approval_request_ids.append(req_id); req_id_counter += 1
            for i in range(random.randint(1, MAX_ITEMS_PER_PARENT)):
                step_id = str(step_id_counter)
                created_step, updated_step = generate_timestamps(datetime.strptime(created, DATETIME_FORMAT))
                step = {
                    "step_id": step_id, "request_id": req_id, "step_order": i + 1, "parallel_group": 1,
                    "assigned_group_id": None, "assigned_user_id": None,
                    "status": request["status"] if request["status"] != 'in_review' else 'pending',
                    "created_at": created_step, "updated_at": updated_step,
                    "due_at": (datetime.strptime(created_step, DATETIME_FORMAT) + timedelta(days=5)).strftime(DATETIME_FORMAT)
                }
                if random.random() > 0.5: step["assigned_user_id"] = random.choice(user_ids)
                else: step["assigned_group_id"] = random.choice(group_ids)
                data["approval_steps"][step_id] = step
                approval_step_ids.append(step_id); step_id_counter += 1

                # Corrected decision logic
                if step['status'] in STATUS_TO_DECISION_MAP:
                    decision_id = str(decision_id_counter)
                    approver = step['assigned_user_id'] or random.choice(user_ids)
                    decision_type = STATUS_TO_DECISION_MAP[step['status']] # Look up correct decision
                    
                    data["approval_decisions"][decision_id] = {
                        "decision_id": decision_id,
                        "step_id": step_id,
                        "approver_user_id": approver,
                        "decision": decision_type,
                        "comment": FREE_FORM_TEXT,
                        "decided_at": updated_step,
                    }
                    decision_id_counter += 1
    print(f"✔️ Generated {len(data['approval_requests'])} approval cycles.")

    # 9. Audit Logs & Notifications
    log_id, notif_id = 1, 1
    for _ in range(len(all_target_entities) * 2):
        target_type, target_id = random.choice(all_target_entities)
        actor = random.choice(user_ids)
        data["audit_logs"][str(log_id)] = {
            "log_id": str(log_id), "actor_user_id": actor, "target_entity_type": target_type, "target_entity_id": target_id,
            "action_type": random.choice(AUDIT_ACTION_TYPES.get(target_type, ['generic_action'])),
            "occurred_at": fake.date_time_between(start_date='-1y').strftime(DATETIME_FORMAT), "details": FREE_FORM_JSON
        }
        log_id += 1
    for _ in range(NUM_USERS * 2):
        recipient = random.choice(user_ids)
        sender = random.choice([u for u in user_ids if u != recipient] + [None])
        recipient_created_at = datetime.strptime(data['users'][recipient]['created_at'], DATETIME_FORMAT)
        created, sent = generate_timestamps(recipient_created_at)
        status = random.choice(NOTIFICATION_STATUSES)
        related_entity = random.choice(all_target_entities) if all_target_entities else (None, None)
        data["notifications"][str(notif_id)] = {
            "notification_id": str(notif_id), "recipient_user_id": recipient,
            "event_type": f"{related_entity[0]}_updated" if related_entity[0] else "system_message",
            "message": FREE_FORM_TEXT, "related_entity_type": related_entity[0], "related_entity_id": related_entity[1],
            "sender_user_id": sender, "channel": random.choice(NOTIFICATION_CHANNELS), "delivery_status": status,
            "created_at": created, "sent_at": sent if status in ['sent', 'read', 'failed'] else None,
            "read_at": fake.date_time_between(datetime.strptime(sent, DATETIME_FORMAT)).strftime(DATETIME_FORMAT) if status == 'read' else None,
            "metadata": FREE_FORM_JSON
        }
        notif_id += 1
    print(f"✔️ Generated audit logs and notifications.")

    # --- FINAL: WRITE TO FILES ---
    output_dir = "generated_data"
    os.makedirs(output_dir, exist_ok=True)
    for table_name, table_data in data.items():
        file_path = os.path.join(output_dir, f"{table_name}.json")
        with open(file_path, 'w') as f:
            json.dump(table_data, f, indent=2)
    print(f"\n✅ Success! All {len(data)} data files have been generated in the '{output_dir}' directory.")

if __name__ == "__main__":
    generate_fake_data()
