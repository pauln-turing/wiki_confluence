"""
Test script for Interface 1 Tools
Demonstrates the functionality of all implemented tools with realistic scenarios.
"""

from tools.interface_1 import *
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def test_user_management():
    """Test user management tools"""
    print("\n=== Testing User Management ===")

    # Create a new user
    new_user = ManageUsers.invoke(
        action="create",
        payload={
            "email": "test.user@example.com",
            "full_name": "Test User",
            "global_role": "content_contributor"
        }
    )
    print(f"✓ Created user: {new_user['user_id']} - {new_user['email']}")

    # Get user by ID
    user = GetUser.invoke(user_id=new_user['user_id'])
    print(f"✓ Retrieved user by ID: {user['full_name']}")

    # Get user by email
    user = GetUser.invoke(email="test.user@example.com")
    print(f"✓ Retrieved user by email: {user['full_name']}")

    # Update user
    updated_user = ManageUsers.invoke(
        action="update",
        payload={
            "user_id": new_user['user_id'],
            "global_role": "space_admin"
        }
    )
    print(f"✓ Updated user role to: {updated_user['global_role']}")

    return new_user['user_id']


def test_group_management(user_id):
    """Test group management tools"""
    print("\n=== Testing Group Management ===")

    # Create a group
    new_group = ManageGroups.invoke(
        action="create",
        payload={"group_name": "Test Engineering Team"}
    )
    print(
        f"✓ Created group: {new_group['group_id']} - {new_group['group_name']}")

    # Get group
    group = GetGroup.invoke(group_id=new_group['group_id'])
    print(f"✓ Retrieved group: {group['group_name']}")

    # Add user to group
    membership = ManageGroupMemberships.invoke(
        action="add",
        payload={
            "user_id": user_id,
            "group_id": new_group['group_id']
        }
    )
    print(f"✓ Added user to group")

    return new_group['group_id']


def test_space_management(user_id):
    """Test space management tools"""
    print("\n=== Testing Space Management ===")

    # Create a space
    new_space = ManageSpaces.invoke(
        action="create",
        payload={
            "space_key": "TEST-SPACE",
            "space_name": "Test Space",
            "space_purpose": "Testing space functionality",
            "created_by_user_id": user_id
        }
    )
    print(
        f"✓ Created space: {new_space['space_id']} - {new_space['space_name']}")

    # Get space
    space = GetSpace.invoke(space_key="TEST-SPACE")
    print(f"✓ Retrieved space: {space['space_name']}")

    # Add space membership
    membership = ManageSpaceMemberships.invoke(
        action="add",
        payload={
            "user_id": user_id,
            "space_id": new_space['space_id'],
            "role": "space_admin"
        }
    )
    print(f"✓ Added user as space admin")

    # Enable space features
    feature = ManageSpaceFeatures.invoke(
        action="manage",
        payload={
            "space_id": new_space['space_id'],
            "feature_type": "whiteboard",
            "is_enabled": True
        }
    )
    print(f"✓ Enabled whiteboard feature")

    return new_space['space_id']


def test_page_management(space_id, user_id):
    """Test page management tools"""
    print("\n=== Testing Page Management ===")

    # Create a page
    new_page = ManagePages.invoke(
        action="create",
        payload={
            "space_id": space_id,
            "title": "Test Page",
            "content_format": "markdown",
            "created_by_user_id": user_id,
            "content_snapshot": "# Test Page\nThis is a test page."
        }
    )
    print(f"✓ Created page: {new_page['page_id']} - {new_page['title']}")

    # Get page
    page = GetPage.invoke(page_id=new_page['page_id'])
    print(f"✓ Retrieved page: {page['title']}")

    # Get page versions
    versions = GetPageVersions.invoke(page_id=new_page['page_id'])
    print(f"✓ Retrieved {len(versions['versions'])} version(s)")

    # Clone page
    cloned_page = ClonePage.invoke(
        payload={
            "source_page_id": new_page['page_id'],
            "target_space_id": space_id,
            "created_by_user_id": user_id,
            "new_title": "Cloned Test Page"
        }
    )
    print(f"✓ Cloned page: {cloned_page['title']}")

    return new_page['page_id']


def test_collaboration(page_id, user_id):
    """Test collaboration tools"""
    print("\n=== Testing Collaboration (Comments) ===")

    # Add comment
    comment = ManageComments.invoke(
        action="add",
        payload={
            "page_id": page_id,
            "comment_text": "This is a test comment",
            "author_user_id": user_id
        }
    )
    print(f"✓ Added comment: {comment['comment_id']}")

    # Get comments
    comments = GetComments.invoke(page_id=page_id)
    print(f"✓ Retrieved {len(comments)} comment(s)")

    return comment['comment_id']


def test_content_management(page_id, user_id):
    """Test content management tools"""
    print("\n=== Testing Content Management ===")

    # Add labels
    labels_result = ManageLabels.invoke(
        action="add",
        payload={
            "page_id": page_id,
            "label_names": ["test", "documentation", "v1.0"]
        }
    )
    print(f"✓ Added {len(labels_result['labels_added'])} label(s)")

    # Get labels
    labels = GetLabels.invoke(page_id=page_id)
    print(f"✓ Retrieved {len(labels)} label(s)")

    # Add attachment
    attachment = ManageAttachments.invoke(
        action="add",
        payload={
            "page_id": page_id,
            "file_name": "test_document.pdf",
            "file_path": "/uploads/test_document.pdf",
            "uploaded_by_user_id": user_id,
            "file_size_bytes": 1024
        }
    )
    print(f"✓ Added attachment: {attachment['file_name']}")

    # Get attachments
    attachments = GetAttachments.invoke(page_id=page_id)
    print(f"✓ Retrieved {len(attachments['attachments'])} attachment(s)")


def test_permissions(page_id, user_id, group_id):
    """Test permission management"""
    print("\n=== Testing Permission Management ===")

    # Grant page permission to user
    permission = ManagePermissions.invoke(
        action="grant",
        payload={
            "page_id": page_id,
            "user_id": user_id,
            "permission_type": "edit",
            "granted_by_user_id": user_id
        }
    )
    print(f"✓ Granted edit permission to user")

    # Grant page permission to group
    permission = ManagePermissions.invoke(
        action="grant",
        payload={
            "page_id": page_id,
            "group_id": group_id,
            "permission_type": "view",
            "granted_by_user_id": user_id
        }
    )
    print(f"✓ Granted view permission to group")

    # Get permissions
    permissions = ManagePermissions.invoke(
        action="get",
        payload={"page_id": page_id}
    )
    print(f"✓ Retrieved {len(permissions['permissions'])} permission(s)")


def test_audit_and_notifications(user_id, space_id):
    """Test audit and notification tools"""
    print("\n=== Testing Audit & Notifications ===")

    # Record audit log
    audit_log = RecordAuditLog.invoke(
        payload={
            "actor_user_id": user_id,
            "action_type": "create_space",
            "target_entity_type": "space",
            "target_entity_id": space_id,
            "details": {"test": "audit log entry"}
        }
    )
    print(f"✓ Recorded audit log: {audit_log['log_id']}")

    # Get audit logs
    logs = GetAuditLog.invoke(actor_user_id=user_id)
    print(f"✓ Retrieved {logs['total_logs']} audit log(s)")

    # Send notification
    notification = SendNotification.invoke(
        payload={
            "recipient_user_id": user_id,
            "event_type": "test_notification",
            "message": "This is a test notification",
            "channel": "system"
        }
    )
    print(f"✓ Sent notification: {notification['notification_id']}")

    # Get notifications
    notifications = GetNotifications.invoke(user_id=user_id)
    print(f"✓ Retrieved {notifications['total']} notification(s)")


def test_approval_workflow(page_id, user_id):
    """Test approval management"""
    print("\n=== Testing Approval Workflow ===")

    # Create approval request
    approval = CreateApprovalRequest.invoke(
        payload={
            "target_entity_type": "page",
            "target_entity_id": page_id,
            "requested_by_user_id": user_id,
            "reason": "Testing approval workflow",
            "steps": [
                {"step_order": 1, "assigned_user_id": user_id}
            ]
        }
    )
    print(f"✓ Created approval request: {approval['request_id']}")
    print(f"  - Created {len(approval['steps_created'])} approval step(s)")

    # Make decision on approval step
    step_id = approval['steps_created'][0]['step_id']
    decision = DecideApprovalStep.invoke(
        payload={
            "step_id": step_id,
            "approver_user_id": user_id,
            "decision": "approve",
            "comment": "Approved for testing"
        }
    )
    print(f"✓ Approved step: {decision['step']['status']}")
    print(f"✓ Request status: {decision['request']['status']}")


def main():
    """Run all tests"""
    print("="*60)
    print("Wiki Confluence Interface 1 Tools - Test Suite")
    print("="*60)

    try:
        # Test each category
        user_id = test_user_management()
        group_id = test_group_management(user_id)
        space_id = test_space_management(user_id)
        page_id = test_page_management(space_id, user_id)
        test_collaboration(page_id, user_id)
        test_content_management(page_id, user_id)
        test_permissions(page_id, user_id, group_id)
        test_audit_and_notifications(user_id, space_id)
        test_approval_workflow(page_id, user_id)

        print("\n" + "="*60)
        print("✓ All tests completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
