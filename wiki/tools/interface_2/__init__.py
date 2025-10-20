from .fetch_config_history import FetchConfigHistory
from .fetch_group import FetchGroup
from .fetch_notifications import FetchNotifications
from .fetch_page import FetchPage
from .fetch_space import FetchSpace
from .fetch_user import FetchUser
from .fetch_watchers import FetchWatchers
from .log_audit_event import LogAuditEvent
from .log_config_change import LogConfigChange
from .notify import Notify
from .request_approval import RequestApproval
from .resolve_approval_step import ResolveApprovalStep
from .set_exports import SetExports
from .set_group_memberships import SetGroupMemberships
from .set_groups import SetGroups
from .set_page_versions import SetPageVersions
from .set_pages import SetPages
from .set_permissions import SetPermissions
from .set_space_features import SetSpaceFeatures
from .set_spaces import SetSpaces
from .set_users import SetUsers
from .set_watchers import SetWatchers

ALL_TOOLS_INTERFACE_2 = [
    FetchConfigHistory,
    FetchGroup,
    FetchNotifications,
    FetchPage,
    FetchSpace,
    FetchUser,
    FetchWatchers,
    LogAuditEvent,
    LogConfigChange,
    Notify,
    RequestApproval,
    ResolveApprovalStep,
    SetExports,
    SetGroupMemberships,
    SetGroups,
    SetPageVersions,
    SetPages,
    SetPermissions,
    SetSpaceFeatures,
    SetSpaces,
    SetUsers,
    SetWatchers
]
