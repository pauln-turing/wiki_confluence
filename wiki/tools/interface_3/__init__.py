from .read_config_history import ReadConfigHistory
from .read_group import ReadGroup
from .read_notifications import ReadNotifications
from .read_page import ReadPage
from .read_space import ReadSpace
from .read_user import ReadUser
from .read_watchers import ReadWatchers
from .update_approval_decision import UpdateApprovalDecision
from .update_approval_request import UpdateApprovalRequest
from .update_audit_log import UpdateAuditLog
from .update_config_change import UpdateConfigChange
from .update_exports import UpdateExports
from .update_group_memberships import UpdateGroupMemberships
from .update_groups import UpdateGroups
from .update_notification import UpdateNotification
from .update_page_versions import UpdatePageVersions
from .update_pages import UpdatePages
from .update_permissions import UpdatePermissions
from .update_space_features import UpdateSpaceFeatures
from .update_spaces import UpdateSpaces
from .update_users import UpdateUsers
from .update_watchers import UpdateWatchers

ALL_TOOLS_INTERFACE_3 = [
    ReadConfigHistory,
    ReadGroup,
    ReadNotifications,
    ReadPage,
    ReadSpace,
    ReadUser,
    ReadWatchers,
    UpdateApprovalDecision,
    UpdateApprovalRequest,
    UpdateAuditLog,
    UpdateConfigChange,
    UpdateExports,
    UpdateGroupMemberships,
    UpdateGroups,
    UpdateNotification,
    UpdatePageVersions,
    UpdatePages,
    UpdatePermissions,
    UpdateSpaceFeatures,
    UpdateSpaces,
    UpdateUsers,
    UpdateWatchers
]
