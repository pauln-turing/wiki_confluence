from .update_page_clone import UpdatePageClone
from .update_approval_request import UpdateApprovalRequest
from .update_approval_decision import UpdateApprovalDecision

from .read_attachments import ReadAttachments
from .read_audit_log import ReadAuditLog
from .read_comments import ReadComments
from .read_config_history import ReadConfigHistory
from .read_group import ReadGroup
from .read_labels import ReadLabels
from .read_notifications import ReadNotifications
from .read_page import ReadPage
from .read_page_versions import ReadPageVersions
from .read_space import ReadSpace
from .read_user import ReadUser
from .read_watchers import ReadWatchers

from .update_attachments import UpdateAttachments
from .update_comments import UpdateComments
from .update_exports import UpdateExports
from .update_group_memberships import UpdateGroupMemberships
from .update_groups import UpdateGroups
from .update_labels import UpdateLabels
from .update_page_versions import UpdatePageVersions
from .update_pages import UpdatePages
from .update_permissions import UpdatePermissions
from .update_space_features import UpdateSpaceFeatures
from .update_space_memberships import UpdateSpaceMemberships
from .update_spaces import UpdateSpaces
from .update_templates import UpdateTemplates
from .update_users import UpdateUsers
from .update_watchers import UpdateWatchers

from .update_page_move import UpdatePageMove
from .update_audit_log import UpdateAuditLog
from .update_config_change import UpdateConfigChange
from .update_notification import UpdateNotification
from .update_template_apply import UpdateTemplateApply


ALL_TOOLS_INTERFACE_3 = [
    UpdatePageClone,
    UpdateApprovalRequest,
    UpdateApprovalDecision,

    ReadAttachments,
    ReadAuditLog,
    ReadComments,
    ReadConfigHistory,
    ReadGroup,
    ReadLabels,
    ReadNotifications,
    ReadPage,
    ReadPageVersions,
    ReadSpace,
    ReadUser,
    ReadWatchers,

    UpdateAttachments,
    UpdateComments,
    UpdateExports,
    UpdateGroupMemberships,
    UpdateGroups,
    UpdateLabels,
    UpdatePageVersions,
    UpdatePages,
    UpdatePermissions,
    UpdateSpaceFeatures,
    UpdateSpaceMemberships,
    UpdateSpaces,
    UpdateTemplates,
    UpdateUsers,
    UpdateWatchers,

    UpdatePageMove,
    UpdateAuditLog,
    UpdateConfigChange,
    UpdateNotification,
    UpdateTemplateApply,
]
