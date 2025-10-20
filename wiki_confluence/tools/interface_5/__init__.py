from .inspect_config_history import InspectConfigHistory
from .inspect_group import InspectGroup
from .inspect_notifications import InspectNotifications
from .inspect_page import InspectPage
from .inspect_space import InspectSpace
from .inspect_user import InspectUser
from .inspect_watchers import InspectWatchers
from .mutate_approval_decision import MutateApprovalDecision
from .mutate_approval_request import MutateApprovalRequest
from .mutate_audit_log import MutateAuditLog
from .mutate_config_change import MutateConfigChange
from .mutate_exports import MutateExports
from .mutate_group_memberships import MutateGroupMemberships
from .mutate_groups import MutateGroups
from .mutate_notification import MutateNotification
from .mutate_page_versions import MutatePageVersions
from .mutate_pages import MutatePages
from .mutate_permissions import MutatePermissions
from .mutate_space_features import MutateSpaceFeatures
from .mutate_spaces import MutateSpaces
from .mutate_users import MutateUsers
from .mutate_watchers import MutateWatchers

ALL_TOOLS_INTERFACE_5 = [
    InspectConfigHistory,
    InspectGroup,
    InspectNotifications,
    InspectPage,
    InspectSpace,
    InspectUser,
    InspectWatchers,
    MutateApprovalDecision,
    MutateApprovalRequest,
    MutateAuditLog,
    MutateConfigChange,
    MutateExports,
    MutateGroupMemberships,
    MutateGroups,
    MutateNotification,
    MutatePageVersions,
    MutatePages,
    MutatePermissions,
    MutateSpaceFeatures,
    MutateSpaces,
    MutateUsers,
    MutateWatchers
]
