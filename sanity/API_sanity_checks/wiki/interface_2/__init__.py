from .duplicate_page import DuplicatePage
from .request_approval import RequestApproval
from .resolve_approval_step import ResolveApprovalStep
from .fetch_attachments import FetchAttachments
from .fetch_audit_log import FetchAuditLog
from .fetch_comments import FetchComments
from .fetch_config_history import FetchConfigHistory
from .fetch_group import FetchGroup
from .fetch_labels import FetchLabels
from .fetch_notifications import FetchNotifications
from .fetch_page import FetchPage
from .fetch_page_versions import FetchPageVersions
from .fetch_space import FetchSpace
from .fetch_user import FetchUser
from .fetch_watchers import FetchWatchers
from .set_attachments import SetAttachments
from .set_comments import SetComments
from .set_exports import SetExports
from .set_group_memberships import SetGroupMemberships
from .set_groups import SetGroups
from .set_labels import SetLabels
from .set_page_versions import SetPageVersions
from .set_pages import SetPages
from .set_permissions import SetPermissions
from .set_space_features import SetSpaceFeatures
from .set_space_memberships import SetSpaceMemberships
from .set_spaces import SetSpaces
from .set_templates import SetTemplates
from .set_users import SetUsers
from .set_watchers import SetWatchers
from .relocate_page import RelocatePage
from .log_audit_event import LogAuditEvent
from .log_config_change import LogConfigChange
from .notify import Notify
from .apply_template import ApplyTemplate

ALL_TOOLS_INTERFACE_2 = [
    DuplicatePage,
    RequestApproval,
    ResolveApprovalStep,
    FetchAttachments,
    FetchAuditLog,
    FetchComments,
    FetchConfigHistory,
    FetchGroup,
    FetchLabels,
    FetchNotifications,
    FetchPage,
    FetchPageVersions,
    FetchSpace,
    FetchUser,
    FetchWatchers,
    SetAttachments,
    SetComments,
    SetExports,
    SetGroupMemberships,
    SetGroups,
    SetLabels,
    SetPageVersions,
    SetPages,
    SetPermissions,
    SetSpaceFeatures,
    SetSpaceMemberships,
    SetSpaces,
    SetTemplates,
    SetUsers,
    SetWatchers,
    RelocatePage,
    LogAuditEvent,
    LogConfigChange,
    Notify,
    ApplyTemplate,
]
