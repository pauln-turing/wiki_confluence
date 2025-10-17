#!/usr/bin/env python3
"""
Wiki Confluence Governance Framework
Implements the comprehensive management policy with role-based access control,
approval workflows, audit logging, and compliance checking.
"""

import json
import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from data_manager import DataManager

class UserRole(Enum):
    GLOBAL_ADMIN = "global_admin"
    SPACE_ADMIN = "space_admin"
    SPACE_MEMBER = "space_member"
    CONTENT_OWNER = "content_owner"
    REVIEWER_APPROVER = "reviewer_approver"
    SECURITY_OFFICER = "security_officer"
    DEVELOPER = "developer"
    ANONYMOUS = "anonymous"
    GUEST = "guest"

class PermissionType(Enum):
    CREATE_SPACE = "create_space"
    UPDATE_SPACE = "update_space"
    DELETE_SPACE = "delete_space"
    MANAGE_SPACE_PERMISSIONS = "manage_space_permissions"
    GRANT_SPACE_ADMIN = "grant_space_admin"
    CONFIGURE_SPACE_SETTINGS = "configure_space_settings"
    EXPORT_SPACE = "export_space"
    IMPORT_SPACE = "import_space"
    CREATE_PAGE = "create_page"
    UPDATE_PAGE = "update_page"
    DELETE_PAGE = "delete_page"
    MOVE_PAGE = "move_page"
    PUBLISH_PAGE = "publish_page"
    UNPUBLISH_PAGE = "unpublish_page"
    MANAGE_PAGE_RESTRICTIONS = "manage_page_restrictions"
    EXPORT_PAGE = "export_page"
    RESTORE_VERSION = "restore_version"
    CLONE_PAGE = "clone_page"
    MANAGE_COMMENTS = "manage_comments"
    MANAGE_LABELS = "manage_labels"
    MANAGE_ATTACHMENTS = "manage_attachments"
    MANAGE_TEMPLATES = "manage_templates"
    MANAGE_WATCHERS = "manage_watchers"
    RECORD_AUDIT_LOG = "record_audit_log"
    RECORD_CONFIG_CHANGE = "record_config_change"
    CREATE_APPROVAL_REQUEST = "create_approval_request"
    DECIDE_APPROVAL_STEP = "decide_approval_step"
    SEND_NOTIFICATION = "send_notification"

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class User:
    user_id: str
    email: str
    full_name: str
    role: UserRole
    permissions: List[PermissionType]
    space_permissions: Dict[str, List[PermissionType]]  # space_key -> permissions
    is_active: bool = True
    created_at: datetime.datetime = None
    last_login: datetime.datetime = None

@dataclass
class ApprovalRequest:
    request_id: str
    requester_id: str
    operation_type: str
    target_entity_type: str
    target_entity_id: str
    payload: Dict[str, Any]
    approvers: List[str]
    status: ApprovalStatus
    created_at: datetime.datetime
    due_at: Optional[datetime.datetime] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AuditLog:
    log_id: str
    actor_user_id: str
    action_type: str
    target_entity_type: str
    target_entity_id: str
    details: Dict[str, Any]
    timestamp: datetime.datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class GovernanceFramework:
    def __init__(self):
        self.data_manager = DataManager()
        self.role_permissions = self._initialize_role_permissions()
        self.approval_workflows = self._initialize_approval_workflows()
    
    def _initialize_role_permissions(self) -> Dict[UserRole, List[PermissionType]]:
        """Initialize role-based permissions according to the policy"""
        return {
            UserRole.GLOBAL_ADMIN: list(PermissionType),
            UserRole.SPACE_ADMIN: [
                PermissionType.UPDATE_SPACE,
                PermissionType.DELETE_SPACE,
                PermissionType.MANAGE_SPACE_PERMISSIONS,
                PermissionType.GRANT_SPACE_ADMIN,
                PermissionType.CONFIGURE_SPACE_SETTINGS,
                PermissionType.EXPORT_SPACE,
                PermissionType.IMPORT_SPACE,
                PermissionType.CREATE_PAGE,
                PermissionType.UPDATE_PAGE,
                PermissionType.DELETE_PAGE,
                PermissionType.MOVE_PAGE,
                PermissionType.PUBLISH_PAGE,
                PermissionType.UNPUBLISH_PAGE,
                PermissionType.MANAGE_PAGE_RESTRICTIONS,
                PermissionType.EXPORT_PAGE,
                PermissionType.RESTORE_VERSION,
                PermissionType.CLONE_PAGE,
                PermissionType.MANAGE_COMMENTS,
                PermissionType.MANAGE_LABELS,
                PermissionType.MANAGE_ATTACHMENTS,
                PermissionType.MANAGE_TEMPLATES,
                PermissionType.MANAGE_WATCHERS,
                PermissionType.RECORD_AUDIT_LOG,
                PermissionType.RECORD_CONFIG_CHANGE,
                PermissionType.CREATE_APPROVAL_REQUEST,
                PermissionType.DECIDE_APPROVAL_STEP,
                PermissionType.SEND_NOTIFICATION
            ],
            UserRole.SPACE_MEMBER: [
                PermissionType.CREATE_PAGE,
                PermissionType.UPDATE_PAGE,
                PermissionType.MANAGE_COMMENTS,
                PermissionType.MANAGE_LABELS,
                PermissionType.MANAGE_ATTACHMENTS,
                PermissionType.MANAGE_WATCHERS,
                PermissionType.CREATE_APPROVAL_REQUEST
            ],
            UserRole.CONTENT_OWNER: [
                PermissionType.UPDATE_PAGE,
                PermissionType.DELETE_PAGE,
                PermissionType.MOVE_PAGE,
                PermissionType.PUBLISH_PAGE,
                PermissionType.UNPUBLISH_PAGE,
                PermissionType.MANAGE_PAGE_RESTRICTIONS,
                PermissionType.EXPORT_PAGE,
                PermissionType.RESTORE_VERSION,
                PermissionType.CLONE_PAGE,
                PermissionType.MANAGE_COMMENTS,
                PermissionType.MANAGE_LABELS,
                PermissionType.MANAGE_ATTACHMENTS,
                PermissionType.MANAGE_WATCHERS
            ],
            UserRole.REVIEWER_APPROVER: [
                PermissionType.DECIDE_APPROVAL_STEP,
                PermissionType.PUBLISH_PAGE,
                PermissionType.UNPUBLISH_PAGE
            ],
            UserRole.SECURITY_OFFICER: [
                PermissionType.MANAGE_SPACE_PERMISSIONS,
                PermissionType.MANAGE_PAGE_RESTRICTIONS,
                PermissionType.RECORD_AUDIT_LOG,
                PermissionType.CREATE_APPROVAL_REQUEST,
                PermissionType.DECIDE_APPROVAL_STEP
            ],
            UserRole.DEVELOPER: [
                PermissionType.CREATE_PAGE,
                PermissionType.UPDATE_PAGE,
                PermissionType.MANAGE_COMMENTS,
                PermissionType.MANAGE_LABELS,
                PermissionType.MANAGE_ATTACHMENTS
            ],
            UserRole.ANONYMOUS: [],
            UserRole.GUEST: []
        }
    
    def _initialize_approval_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Initialize approval workflows for different operations"""
        return {
            "create_space": {
                "requires_approval": True,
                "approvers": ["global_admin", "security_officer"],
                "timeout_hours": 24
            },
            "delete_space": {
                "requires_approval": True,
                "approvers": ["global_admin"],
                "timeout_hours": 48
            },
            "manage_space_permissions": {
                "requires_approval": True,
                "approvers": ["space_admin", "security_officer"],
                "timeout_hours": 12
            },
            "publish_page": {
                "requires_approval": False,
                "approvers": [],
                "timeout_hours": None
            },
            "export_space": {
                "requires_approval": False,
                "approvers": [],
                "timeout_hours": None
            }
        }
    
    def validate_user_permission(self, user_id: str, permission: PermissionType, 
                               space_key: Optional[str] = None) -> Tuple[bool, str]:
        """Validate if user has permission for an operation"""
        try:
            # Get user information
            user_data = self.data_manager.find_by_field("users", "user_id", user_id)
            if not user_data:
                return False, "User not found"
            
            user_role = UserRole(user_data.get("role", "space_member"))
            
            # Check global permissions
            if permission in self.role_permissions.get(user_role, []):
                return True, "Permission granted"
            
            # Check space-specific permissions
            if space_key and space_key in user_data.get("space_permissions", {}):
                space_perms = user_data["space_permissions"][space_key]
                if permission.value in space_perms:
                    return True, "Space permission granted"
            
            return False, f"User role '{user_role.value}' does not have permission '{permission.value}'"
            
        except Exception as e:
            return False, f"Error validating permission: {str(e)}"
    
    def check_approval_required(self, operation_type: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if an operation requires approval"""
        workflow = self.approval_workflows.get(operation_type, {})
        requires_approval = workflow.get("requires_approval", False)
        return requires_approval, workflow
    
    def create_approval_request(self, requester_id: str, operation_type: str, 
                              target_entity_type: str, target_entity_id: str,
                              payload: Dict[str, Any], reason: Optional[str] = None) -> str:
        """Create an approval request"""
        request_id = self.data_manager.get_next_id("approval_requests")
        
        requires_approval, workflow = self.check_approval_required(operation_type)
        if not requires_approval:
            return None  # No approval needed
        
        approval_request = ApprovalRequest(
            request_id=request_id,
            requester_id=requester_id,
            operation_type=operation_type,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            payload=payload,
            approvers=workflow.get("approvers", []),
            status=ApprovalStatus.PENDING,
            created_at=datetime.datetime.now(),
            due_at=datetime.datetime.now() + datetime.timedelta(
                hours=workflow.get("timeout_hours", 24)
            ) if workflow.get("timeout_hours") else None,
            reason=reason
        )
        
        # Save approval request
        self.data_manager.create_record("approval_requests", request_id, {
            "request_id": request_id,
            "requester_id": requester_id,
            "operation_type": operation_type,
            "target_entity_type": target_entity_type,
            "target_entity_id": target_entity_id,
            "payload": payload,
            "approvers": workflow.get("approvers", []),
            "status": ApprovalStatus.PENDING.value,
            "created_at": approval_request.created_at.isoformat(),
            "due_at": approval_request.due_at.isoformat() if approval_request.due_at else None,
            "reason": reason
        })
        
        return request_id
    
    def record_audit_log(self, actor_user_id: str, action_type: str, 
                        target_entity_type: str, target_entity_id: str,
                        details: Dict[str, Any], ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None) -> str:
        """Record an audit log entry"""
        log_id = self.data_manager.get_next_id("audit_logs")
        
        audit_log = AuditLog(
            log_id=log_id,
            actor_user_id=actor_user_id,
            action_type=action_type,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            details=details,
            timestamp=datetime.datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Save audit log
        self.data_manager.create_record("audit_logs", log_id, {
            "log_id": log_id,
            "actor_user_id": actor_user_id,
            "action_type": action_type,
            "target_entity_type": target_entity_type,
            "target_entity_id": target_entity_id,
            "details": details,
            "timestamp": audit_log.timestamp.isoformat(),
            "ip_address": ip_address,
            "user_agent": user_agent
        })
        
        return log_id
    
    def validate_space_exists(self, space_key: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate if space exists"""
        try:
            space_data = self.data_manager.find_by_field("spaces", "space_key", space_key)
            if space_data:
                return True, space_data
            return False, None
        except Exception as e:
            return False, None
    
    def validate_page_exists(self, page_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate if page exists"""
        try:
            page_data = self.data_manager.get_record("pages", page_id)
            if page_data:
                return True, page_data
            return False, None
        except Exception as e:
            return False, None
    
    def validate_user_exists(self, user_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate if user exists"""
        try:
            user_data = self.data_manager.find_by_field("users", "user_id", user_id)
            if user_data:
                return True, user_data
            return False, None
        except Exception as e:
            return False, None
    
    def check_data_classification(self, content: str) -> DataClassification:
        """Check data classification based on content"""
        # Simple classification logic - in production this would be more sophisticated
        sensitive_keywords = ["confidential", "restricted", "internal", "private"]
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ["confidential", "restricted"]):
            return DataClassification.RESTRICTED
        elif any(keyword in content_lower for keyword in ["internal", "private"]):
            return DataClassification.CONFIDENTIAL
        else:
            return DataClassification.PUBLIC
    
    def enforce_retention_policy(self, entity_type: str, entity_id: str) -> bool:
        """Check if entity should be retained based on retention policy"""
        # Simple retention logic - in production this would be more sophisticated
        return True  # For now, retain everything
    
    def validate_naming_convention(self, name: str, entity_type: str) -> Tuple[bool, str]:
        """Validate naming conventions"""
        if entity_type == "space":
            # Space naming conventions
            if len(name) < 3:
                return False, "Space name must be at least 3 characters"
            if not name.replace("_", "").replace("-", "").isalnum():
                return False, "Space name can only contain alphanumeric characters, hyphens, and underscores"
        elif entity_type == "page":
            # Page naming conventions
            if len(name) < 1:
                return False, "Page title cannot be empty"
        
        return True, "Valid naming convention"
