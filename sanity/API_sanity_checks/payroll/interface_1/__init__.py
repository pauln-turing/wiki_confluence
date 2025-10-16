from .add_audit_logs_entry import AddAuditLogsEntry
from .create_approval_request import CreateApprovalRequest
from .create_dispute import CreateDispute
from .create_employee import CreateEmployee
from .create_invoice import CreateInvoice
from .create_offboarding_request import CreateOffboardingRequest
from .create_payment import CreatePayment
from .create_payroll_run import CreatePayrollRun
from .create_vendor import CreateVendor
from .execute_external_payment import ExecuteExternalPayment
from .generate_employee_pays import GenerateEmployeePays
from .get_approval_request import GetApprovalRequest
from .get_audit_entries_for_entity import GetAuditEntriesForEntity
from .get_department import GetDepartment
from .get_dispute import GetDispute
from .get_employee import GetEmployee
from .get_employee_pay import GetEmployeePay
from .get_invoice import GetInvoice
from .get_offboarding_request import GetOffboardingRequest
from .get_onboarding_request import GetOnboardingRequest
from .get_order import GetOrder
from .get_payment import GetPayment
from .get_payroll_run import GetPayrollRun
from .get_pending_approvals import GetPendingApprovals
from .get_vendor import GetVendor
from .query_table import QueryTable
from .resolve_dispute import ResolveDispute
from .submit_approval_decision import SubmitApprovalDecision
from .update_dispute_status import UpdateDisputeStatus
from .update_employee import UpdateEmployee
from .update_employee_pay import UpdateEmployeePay
from .update_invoice import UpdateInvoice
from .update_offboarding_request import UpdateOffboardingRequest
from .update_onboarding_request import UpdateOnboardingRequest
from .update_payment import UpdatePayment
from .update_vendor import UpdateVendor

ALL_TOOLS_INTERFACE_1 = [
    AddAuditLogsEntry,
    CreateApprovalRequest,
    CreateDispute,
    CreateEmployee,
    CreateInvoice,
    CreateOffboardingRequest,
    CreatePayment,
    CreatePayrollRun,
    CreateVendor,
    ExecuteExternalPayment,
    GenerateEmployeePays,
    GetApprovalRequest,
    GetAuditEntriesForEntity,
    GetDepartment,
    GetDispute,
    GetEmployee,
    GetEmployeePay,
    GetInvoice,
    GetOffboardingRequest,
    GetOnboardingRequest,
    GetOrder,
    GetPayment,
    GetPayrollRun,
    GetPendingApprovals,
    GetVendor,
    QueryTable,
    ResolveDispute,
    SubmitApprovalDecision,
    UpdateDisputeStatus,
    UpdateEmployee,
    UpdateEmployeePay,
    UpdateInvoice,
    UpdateOffboardingRequest,
    UpdateOnboardingRequest,
    UpdatePayment,
    UpdateVendor
]
