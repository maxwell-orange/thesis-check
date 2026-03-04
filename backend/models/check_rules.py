"""
Check rules definitions for thesis format checking
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class IssueType(Enum):
    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"


class IssueCategory(Enum):
    PAGE_SETUP = "页面设置"
    CHAPTER_TITLE = "章标题格式"
    SECTION_TITLE = "节标题格式"
    SUBSECTION_TITLE = "小节标题格式"
    BODY_TEXT = "正文格式"
    ABSTRACT = "摘要格式"
    REFERENCE = "参考文献格式"
    REFERENCE_AUTHORITY = "参考文献真实性"
    REFERENCE_CITATION = "引用匹配"
    REFERENCE_FORMAT = "格式规范"
    FIGURE_TABLE = "图表格式"
    CONTENT = "内容质量"
    LANGUAGE = "语言表达"
    CITATION = "引用规范"


@dataclass
class FormatIssue:
    """Format issue data class"""
    type: str  # "error" | "warning" | "suggestion"
    category: str
    location: str
    message: str
    suggestion: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'category': self.category,
            'location': self.location,
            'message': self.message,
            'suggestion': self.suggestion,
            'details': self.details or {}
        }


@dataclass
class AIIssue:
    """AI check issue data class"""
    type: str
    location: str
    original_text: str
    issue_description: str
    suggestion: str
    corrected_text: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'location': self.location,
            'original_text': self.original_text,
            'issue_description': self.issue_description,
            'suggestion': self.suggestion,
            'corrected_text': self.corrected_text or ''
        }


@dataclass
class CheckSummary:
    """Check summary data class"""
    total_issues: int
    error_count: int
    warning_count: int
    suggestion_count: int
    overall_evaluation: str

    def to_dict(self) -> Dict:
        return {
            'total_issues': self.total_issues,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'suggestion_count': self.suggestion_count,
            'overall_evaluation': self.overall_evaluation
        }


# Format check rules definition
FORMAT_CHECK_RULES = {
    'page_setup': {
        'name': '页面设置',
        'rules': [
            {'name': '纸张大小', 'expected': 'A4', 'priority': 'high'},
            {'name': '上边距', 'expected': '2.5cm', 'min': 2.4, 'max': 2.6, 'priority': 'high'},
            {'name': '下边距', 'expected': '2.0cm', 'min': 1.9, 'max': 2.1, 'priority': 'high'},
            {'name': '左边距', 'expected': '2.5cm', 'min': 2.4, 'max': 2.6, 'priority': 'high'},
            {'name': '右边距', 'expected': '2.0cm', 'min': 1.9, 'max': 2.1, 'priority': 'high'},
        ]
    },
    'chapter_title': {
        'name': '章标题格式',
        'rules': [
            {'name': '字体', 'expected': '黑体', 'priority': 'high'},
            {'name': '字号', 'expected': '三号(16pt)', 'expected_pt': 16, 'tolerance': 0.5, 'priority': 'high'},
            {'name': '加粗', 'expected': True, 'priority': 'high'},
            {'name': '对齐', 'expected': '居中', 'priority': 'high'},
            {'name': '段前间距', 'expected': '0.5行', 'priority': 'medium'},
            {'name': '段后间距', 'expected': '0.5行', 'priority': 'medium'},
        ]
    },
    'section_title': {
        'name': '节标题格式',
        'rules': [
            {'name': '字体', 'expected': '黑体', 'priority': 'high'},
            {'name': '字号', 'expected': '四号(14pt)', 'expected_pt': 14, 'tolerance': 0.5, 'priority': 'high'},
            {'name': '加粗', 'expected': True, 'priority': 'high'},
            {'name': '对齐', 'expected': '左对齐', 'priority': 'high'},
            {'name': '段前间距', 'expected': '0.5行', 'priority': 'medium'},
            {'name': '段后间距', 'expected': '0.5行', 'priority': 'medium'},
        ]
    },
    'subsection_title': {
        'name': '小节标题格式',
        'rules': [
            {'name': '字体', 'expected': '黑体', 'priority': 'high'},
            {'name': '字号', 'expected': '小四(12pt)', 'expected_pt': 12, 'tolerance': 0.5, 'priority': 'high'},
            {'name': '加粗', 'expected': True, 'priority': 'high'},
            {'name': '首行缩进', 'expected': '2字符', 'priority': 'high'},
            {'name': '段前间距', 'expected': '0.5行', 'priority': 'medium'},
            {'name': '段后间距', 'expected': '0.5行', 'priority': 'medium'},
        ]
    },
    'body_text': {
        'name': '正文格式',
        'rules': [
            {'name': '中文字体', 'expected': '宋体', 'priority': 'high'},
            {'name': '英文字体', 'expected': 'Times New Roman', 'priority': 'high'},
            {'name': '字号', 'expected': '小四(12pt)', 'expected_pt': 12, 'tolerance': 0.5, 'priority': 'high'},
            {'name': '首行缩进', 'expected': '2字符', 'priority': 'high'},
            {'name': '行距', 'expected': '1.5倍', 'expected_spacing': 1.5, 'tolerance': 0.1, 'priority': 'high'},
        ]
    },
    'abstract': {
        'name': '摘要格式',
        'rules': [
            {'name': '中文字数', 'expected': '300字左右', 'min': 250, 'max': 350, 'priority': 'high'},
            {'name': '英文字数', 'expected': '与中文对应', 'priority': 'medium'},
            {'name': '字体', 'expected': '宋体', 'priority': 'medium'},
            {'name': '字号', 'expected': '小四', 'priority': 'medium'},
        ]
    },
    'references': {
        'name': '参考文献',
        'rules': [
            {'name': '数量', 'expected': '≥10篇', 'min': 10, 'priority': 'high'},
            {'name': '近三年比例', 'expected': '≥30%', 'min_ratio': 0.3, 'priority': 'high'},
            {'name': '格式标准', 'expected': 'GB/T 7714', 'priority': 'high'},
        ]
    }
}
