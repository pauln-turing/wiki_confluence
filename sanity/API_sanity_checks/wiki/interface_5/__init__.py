from .mutate_page_clone import MutatePageClone
from .mutate_approval_request import MutateApprovalRequest
from .mutate_approval_decision import MutateApprovalDecision

from .inspect_attachments import InspectAttachments
from .inspect_audit_log import InspectAuditLog
from .inspect_comments import InspectComments
from .inspect_config_history import InspectConfigHistory
from .inspect_group import InspectGroup
from .inspect_labels import InspectLabels
from .inspect_notifications import InspectNotifications
from .inspect_page import InspectPage
from .inspect_page_versions import InspectPageVersions
from .inspect_space import InspectSpace
from .inspect_user import InspectUser
from .inspect_watchers import InspectWatchers

from .mutate_attachments import MutateAttachments
from .mutate_comments import MutateComments
from .mutate_exports import MutateExports
from .mutate_group_memberships import MutateGroupMemberships
from .mutate_groups import MutateGroups
from .mutate_labels import MutateLabels
from .mutate_page_versions import MutatePageVersions
from .mutate_pages import MutatePages
from .mutate_permissions import MutatePermissions
from .mutate_space_features import MutateSpaceFeatures
from .mutate_space_memberships import MutateSpaceMemberships
from .mutate_spaces import MutateSpaces
from .mutate_templates import MutateTemplates
from .mutate_users import MutateUsers
from .mutate_watchers import MutateWatchers

from .mutate_page_move import MutatePageMove
from .mutate_audit_log import MutateAuditLog
from .mutate_config_change import MutateConfigChange
from .mutate_notification import MutateNotification
from .mutate_template_apply import MutateTemplateApply


ALL_TOOLS_INTERFACE_5 = [
    MutatePageClone,
    MutateApprovalRequest,
    MutateApprovalDecision,

    InspectAttachments,
    InspectAuditLog,
    InspectComments,
    InspectConfigHistory,
    InspectGroup,
    InspectLabels,
    InspectNotifications,
    InspectPage,
    InspectPageVersions,
    InspectSpace,
    InspectUser,
    InspectWatchers,

    MutateAttachments,
    MutateComments,
    MutateExports,
    MutateGroupMemberships,
    MutateGroups,
    MutateLabels,
    MutatePageVersions,
    MutatePages,
    MutatePermissions,
    MutateSpaceFeatures,
    MutateSpaceMemberships,
    MutateSpaces,
    MutateTemplates,
    MutateUsers,
    MutateWatchers,
    MutatePageMove,
    MutateAuditLog,
    MutateConfigChange,
    MutateNotification,
    MutateTemplateApply,
]
