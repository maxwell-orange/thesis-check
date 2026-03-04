"""
Report data models
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


@dataclass
class FormatCheckResult:
    """Format check result"""
    status: str = "pending"  # pending, processing, completed, failed
    issues: List[Dict] = field(default_factory=list)
    issue_count: int = 0
    check_time: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'status': self.status,
            'issues': self.issues,
            'issue_count': len(self.issues),
            'check_time': self.check_time,
            'error_message': self.error_message
        }


@dataclass
class AICheckResult:
    """AI check result"""
    status: str = "pending"
    issues: List[Dict] = field(default_factory=list)
    issue_count: int = 0
    summary: Optional[Dict] = None
    check_time: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'status': self.status,
            'issues': self.issues,
            'issue_count': len(self.issues),
            'summary': self.summary,
            'check_time': self.check_time,
            'error_message': self.error_message
        }


@dataclass
class CheckReport:
    """Complete check report"""
    check_id: str
    file_id: str
    file_name: str
    status: str = "pending"  # pending, processing, completed, failed
    check_time: Optional[str] = None
    format_check: FormatCheckResult = field(default_factory=FormatCheckResult)
    ai_check: AICheckResult = field(default_factory=AICheckResult)
    total_issues: int = 0

    def __post_init__(self):
        if self.check_id is None:
            self.check_id = str(uuid.uuid4())
        if self.check_time is None:
            self.check_time = datetime.now().isoformat()

    def update_total_issues(self):
        """Update total issue count"""
        self.total_issues = (
            len(self.format_check.issues) +
            len(self.ai_check.issues)
        )

    def to_dict(self) -> Dict:
        self.update_total_issues()
        return {
            'check_id': self.check_id,
            'file_id': self.file_id,
            'file_name': self.file_name,
            'status': self.status,
            'check_time': self.check_time,
            'format_check': self.format_check.to_dict(),
            'ai_check': self.ai_check.to_dict(),
            'total_issues': self.total_issues
        }


# In-memory storage for reports (use database in production)
_report_storage: Dict[str, CheckReport] = {}


def save_report(report: CheckReport):
    """Save report to storage"""
    _report_storage[report.check_id] = report


def get_report(check_id: str) -> Optional[CheckReport]:
    """Get report by check_id"""
    return _report_storage.get(check_id)


def delete_report(check_id: str) -> bool:
    """Delete report by check_id"""
    if check_id in _report_storage:
        del _report_storage[check_id]
        return True
    return False


def get_all_reports() -> List[CheckReport]:
    """Get all reports"""
    return list(_report_storage.values())
