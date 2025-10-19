# tools/interface_4/__init__.py

from .commit_page_clone import CommitPageClone
from .commit_approval_request import CommitApprovalRequest
from .commit_approval_decision import CommitApprovalDecision

from .lookup_attachments import LookupAttachments
from .lookup_audit_log import LookupAuditLog
from .lookup_comments import LookupComments
from .lookup_config_history import LookupConfigHistory
from .lookup_group import LookupGroup
from .lookup_labels import LookupLabels
from .lookup_notifications import LookupNotifications
from .lookup_page import LookupPage
from .lookup_page_versions import LookupPageVersions
from .lookup_space import LookupSpace
from .lookup_user import LookupUser
from .lookup_watchers import LookupWatchers

from .commit_attachments import CommitAttachments
from .commit_comments import CommitComments
from .commit_exports import CommitExports
from .commit_group_memberships import CommitGroupMemberships
from .commit_groups import CommitGroups
from .commit_labels import CommitLabels
from .commit_page_versions import CommitPageVersions
from .commit_pages import CommitPages
from .commit_permissions import CommitPermissions
from .commit_space_features import CommitSpaceFeatures
from .commit_space_memberships import CommitSpaceMemberships
from .commit_spaces import CommitSpaces
from .commit_templates import CommitTemplates
from .commit_users import CommitUsers
from .commit_watchers import CommitWatchers

from .commit_page_move import CommitPageMove
from .commit_audit_log import CommitAuditLog
from .commit_config_change import CommitConfigChange
from .commit_notification import CommitNotification
from .commit_template_apply import CommitTemplateApply


ALL_TOOLS_INTERFACE_4 = [
    CommitPageClone,
    CommitApprovalRequest,
    CommitApprovalDecision,

    LookupAttachments,
    LookupAuditLog,
    LookupComments,
    LookupConfigHistory,
    LookupGroup,
    LookupLabels,
    LookupNotifications,
    LookupPage,
    LookupPageVersions,
    LookupSpace,
    LookupUser,
    LookupWatchers,

    CommitAttachments,
    CommitComments,
    CommitExports,
    CommitGroupMemberships,
    CommitGroups,
    CommitLabels,
    CommitPageVersions,
    CommitPages,
    CommitPermissions,
    CommitSpaceFeatures,
    CommitSpaceMemberships,
    CommitSpaces,
    CommitTemplates,
    CommitUsers,
    CommitWatchers,

    CommitPageMove,
    CommitAuditLog,
    CommitConfigChange,
    CommitNotification,
    CommitTemplateApply,
]
