"""
PDF Report Generator for thesis check system
Uses reportlab library to generate PDF reports with Chinese font support
"""
import os
import io
from datetime import datetime
from typing import Dict, List, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class PDFReportGenerator:
    """PDF Report Generator for thesis check reports using ReportLab"""

    # Colors
    COLOR_ERROR = colors.HexColor('#DC3545')
    COLOR_WARNING = colors.HexColor('#FFC107')
    COLOR_SUGGESTION = colors.HexColor('#0D6EFD')
    COLOR_SUCCESS = colors.HexColor('#198754')
    COLOR_HEADER = colors.HexColor('#212529')
    COLOR_TEXT = colors.HexColor('#333333')
    COLOR_LIGHT_BG = colors.HexColor('#F8F9FA')
    COLOR_BORDER = colors.HexColor('#DEE2E6')

    def __init__(self, fonts_dir: str = None):
        self.fonts_dir = fonts_dir or os.path.join(os.path.dirname(__file__), '..', 'fonts')
        self.styles = getSampleStyleSheet()
        self._setup_fonts()
        self._setup_styles()

    def _setup_fonts(self):
        """Setup Chinese fonts for PDF"""
        self.has_chinese_fonts = False
        self.font_name = 'Helvetica'
        self.font_name_bold = 'Helvetica-Bold'

        # Try to find and register Chinese fonts
        font_paths = self._find_fonts()

        if font_paths['regular']:
            try:
                pdfmetrics.registerFont(TTFont('Chinese', font_paths['regular']))
                self.font_name = 'Chinese'
                self.has_chinese_fonts = True
                print(f"Registered Chinese font: {font_paths['regular']}")
            except Exception as e:
                print(f"Warning: Failed to register Chinese font: {e}")

        if font_paths['bold']:
            try:
                pdfmetrics.registerFont(TTFont('ChineseBold', font_paths['bold']))
                self.font_name_bold = 'ChineseBold'
                if not self.has_chinese_fonts:
                    self.font_name = 'ChineseBold'
                self.has_chinese_fonts = True
                print(f"Registered Chinese bold font: {font_paths['bold']}")
            except Exception as e:
                print(f"Warning: Failed to register Chinese bold font: {e}")

    def _find_fonts(self) -> Dict[str, Optional[str]]:
        """Find available font files"""
        font_paths = {'regular': None, 'bold': None}

        # First, check for bundled Chinese fonts in fonts_dir (priority)
        # Try TTC fonts first (better compatibility with reportlab)
        bundled_ttc = os.path.join(self.fonts_dir, 'wqy-microhei.ttc')
        if os.path.exists(bundled_ttc):
            font_paths['regular'] = bundled_ttc
            font_paths['bold'] = bundled_ttc
            print(f"Found bundled TTC font: {bundled_ttc}")
            return font_paths

        # Try OTF fonts (Noto Sans CJK)
        bundled_regular = os.path.join(self.fonts_dir, 'NotoSansCJKsc-Regular.otf')
        bundled_bold = os.path.join(self.fonts_dir, 'NotoSansCJKsc-Bold.otf')

        if os.path.exists(bundled_regular):
            font_paths['regular'] = bundled_regular
            print(f"Found bundled regular font: {bundled_regular}")

        if os.path.exists(bundled_bold):
            font_paths['bold'] = bundled_bold
            print(f"Found bundled bold font: {bundled_bold}")

        # If we found both fonts, return early
        if font_paths['regular'] and font_paths['bold']:
            return font_paths

        # Otherwise, search in system directories
        # Common font file locations
        search_paths = [
            '/usr/share/fonts/truetype/wqy/',
            '/usr/share/fonts/truetype/noto/',
            '/usr/share/fonts/opentype/noto/',
            '/usr/share/fonts/truetype/dejavu/',
            '/usr/share/fonts/truetype/liberation/',
            '/System/Library/Fonts/',
            '/Library/Fonts/',
            os.path.expanduser('~/.fonts/'),
        ]

        # Font file patterns to search for ( prioritize CJK fonts)
        regular_patterns = [
            'NotoSansCJKsc-Regular.otf',
            'NotoSansCJK-Regular.ttc',
            'wqy-zenhei.ttc',
            'wqy-microhei.ttc',
            'DejaVuSans.ttf',
            'LiberationSans-Regular.ttf',
            'SimSun.ttf',
            'simsun.ttf',
        ]

        bold_patterns = [
            'NotoSansCJKsc-Bold.otf',
            'NotoSansCJK-Bold.ttc',
            'wqy-zenhei.ttc',
            'DejaVuSans-Bold.ttf',
            'LiberationSans-Bold.ttf',
            'SimHei.ttf',
            'simhei.ttf',
        ]

        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue

            try:
                for filename in os.listdir(search_path):
                    filepath = os.path.join(search_path, filename)
                    if not os.path.isfile(filepath):
                        continue

                    # Check for regular fonts
                    if font_paths['regular'] is None:
                        for pattern in regular_patterns:
                            if pattern.lower() in filename.lower():
                                font_paths['regular'] = filepath
                                break

                    # Check for bold fonts
                    if font_paths['bold'] is None:
                        for pattern in bold_patterns:
                            if pattern.lower() in filename.lower():
                                font_paths['bold'] = filepath
                                break
            except (OSError, PermissionError):
                continue

        return font_paths

    def _setup_styles(self):
        """Setup paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            fontName=self.font_name_bold,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=self.COLOR_HEADER,
        ))

        # Heading style
        self.styles.add(ParagraphStyle(
            name='ChineseHeading',
            fontName=self.font_name_bold,
            fontSize=14,
            alignment=TA_LEFT,
            spaceBefore=15,
            spaceAfter=10,
            textColor=self.COLOR_HEADER,
        ))

        # Normal text style
        self.styles.add(ParagraphStyle(
            name='ChineseNormal',
            fontName=self.font_name,
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6,
            textColor=self.COLOR_TEXT,
            leading=14,
        ))

        # Small text style
        self.styles.add(ParagraphStyle(
            name='ChineseSmall',
            fontName=self.font_name,
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=4,
            textColor=self.COLOR_TEXT,
            leading=12,
        ))

    def generate_report(self, report_data: Dict[str, Any]) -> bytes:
        """Generate PDF report from report data"""
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        # Build document content
        story = []

        # Add report sections
        self._add_header(story, report_data)
        self._add_summary(story, report_data)

        # Add format check results if available
        format_check = report_data.get('format_check', {})
        if format_check.get('issues'):
            self._add_format_issues(story, format_check['issues'])

        # Add AI check results if available
        ai_check = report_data.get('ai_check', {})
        if ai_check.get('issues'):
            self._add_ai_issues(story, ai_check['issues'])

        # Add footer
        self._add_footer(story, report_data)

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def _add_header(self, story: List, report_data: Dict[str, Any]):
        """Add report header with title"""
        # Title
        story.append(Paragraph("山东财经大学计算机与人工智能学院本科毕业论文检查报告", self.styles['ChineseTitle']))
        story.append(Spacer(1, 0.3*cm))

        # File info
        file_name = report_data.get('file_name', '未知文件')
        check_time = report_data.get('check_time', datetime.now().isoformat())

        story.append(Paragraph(f"文件名: {file_name}", self.styles['ChineseNormal']))
        story.append(Paragraph(f"检查时间: {self._format_datetime(check_time)}", self.styles['ChineseNormal']))
        story.append(Spacer(1, 0.5*cm))

        # Separator line (using a table with border)
        line_table = Table([['']], colWidths=[17*cm])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 1, self.COLOR_BORDER),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 0.5*cm))

    def _add_summary(self, story: List, report_data: Dict[str, Any]):
        """Add problem summary section"""
        story.append(Paragraph("问题统计", self.styles['ChineseHeading']))

        # Calculate statistics
        format_check = report_data.get('format_check', {})
        ai_check = report_data.get('ai_check', {})

        format_issues = format_check.get('issues', [])
        ai_issues = ai_check.get('issues', [])

        error_count = (
            sum(1 for i in format_issues if i.get('type') == 'error') +
            sum(1 for i in ai_issues if i.get('type') == 'error')
        )
        warning_count = (
            sum(1 for i in format_issues if i.get('type') == 'warning') +
            sum(1 for i in ai_issues if i.get('type') == 'warning')
        )
        suggestion_count = (
            sum(1 for i in format_issues if i.get('type') == 'suggestion') +
            sum(1 for i in ai_issues if i.get('type') == 'suggestion')
        )
        total = error_count + warning_count + suggestion_count

        # Create summary table
        summary_data = [
            ['总问题数', '错误', '警告', '建议'],
            [str(total), str(error_count), str(warning_count), str(suggestion_count)],
        ]

        summary_table = Table(summary_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_LIGHT_BG),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_HEADER),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # Value row
            ('FONTNAME', (0, 1), (-1, 1), self.font_name_bold),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
            ('TOPPADDING', (0, 1), (-1, 1), 12),

            # Colors for values
            ('TEXTCOLOR', (0, 1), (0, 1), self.COLOR_HEADER),
            ('TEXTCOLOR', (1, 1), (1, 1), self.COLOR_ERROR),
            ('TEXTCOLOR', (2, 1), (2, 1), self.COLOR_WARNING),
            ('TEXTCOLOR', (3, 1), (3, 1), self.COLOR_SUGGESTION),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLOR_BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 0.5*cm))

        # AI summary if available
        ai_summary = ai_check.get('summary', {})
        if ai_summary.get('overall_evaluation'):
            story.append(Paragraph("AI 总体评价", self.styles['ChineseHeading']))
            story.append(Paragraph(
                ai_summary['overall_evaluation'],
                self.styles['ChineseNormal']
            ))
            story.append(Spacer(1, 0.3*cm))

    def _add_format_issues(self, story: List, issues: List[Dict[str, Any]]):
        """Add format issues section"""
        if not issues:
            return

        story.append(Paragraph(f"格式问题 ({len(issues)}项)", self.styles['ChineseHeading']))

        for issue in issues:
            issue_elements = self._create_issue_elements(issue, 'format')
            story.append(KeepTogether(issue_elements))

    def _add_ai_issues(self, story: List, issues: List[Dict[str, Any]]):
        """Add AI check issues section"""
        if not issues:
            return

        story.append(PageBreak())
        story.append(Paragraph(f"AI 检查问题 ({len(issues)}项)", self.styles['ChineseHeading']))

        for issue in issues:
            issue_elements = self._create_issue_elements(issue, 'ai')
            story.append(KeepTogether(issue_elements))

    def _create_issue_elements(self, issue: Dict[str, Any], issue_type: str) -> List:
        """Create elements for a single issue"""
        elements = []

        issue_type_code = issue.get('type', 'suggestion')
        type_label = {'error': '错误', 'warning': '警告', 'suggestion': '建议'}.get(issue_type_code, '建议')
        type_color = {
            'error': self.COLOR_ERROR,
            'warning': self.COLOR_WARNING,
            'suggestion': self.COLOR_SUGGESTION
        }.get(issue_type_code, self.COLOR_SUGGESTION)

        # Type badge and category
        category = issue.get('category', '其他')

        # Create type badge table
        badge_data = [[type_label, category]]
        badge_table = Table(badge_data, colWidths=[2*cm, 14*cm])
        badge_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), type_color),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('FONTNAME', (0, 0), (0, 0), self.font_name_bold),
            ('FONTSIZE', (0, 0), (0, 0), 9),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),

            ('FONTNAME', (1, 0), (1, 0), self.font_name_bold),
            ('FONTSIZE', (1, 0), (1, 0), 10),
            ('LEFTPADDING', (1, 0), (1, 0), 8),
            ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
        ]))
        elements.append(badge_table)
        elements.append(Spacer(1, 0.2*cm))

        # Location
        location = issue.get('location', '')
        if location:
            elements.append(Paragraph(
                f"<font color='#666666'>位置: {location}</font>",
                self.styles['ChineseSmall']
            ))

        # Message / Description
        if issue_type == 'format':
            message = issue.get('message', '')
        else:
            message = issue.get('issue_description', issue.get('message', ''))

        if message:
            elements.append(Paragraph(
                f"<b>问题:</b> {message}",
                self.styles['ChineseNormal']
            ))

        # Original text for AI issues
        if issue_type == 'ai':
            original_text = issue.get('original_text', '')
            if original_text:
                # Truncate if too long
                if len(original_text) > 200:
                    original_text = original_text[:200] + '...'
                elements.append(Paragraph(
                    f"<font color='#555555'><i>原文: \"{original_text}\"</i></font>",
                    self.styles['ChineseSmall']
                ))

        # Suggestion
        suggestion = issue.get('suggestion', '')
        if suggestion:
            success_color = self.COLOR_SUCCESS.hexval()[2:8]
            elements.append(Paragraph(
                f"<font color='#{success_color}'><b>建议:</b> {suggestion}</font>",
                self.styles['ChineseNormal']
            ))

        # Corrected text for AI issues
        if issue_type == 'ai':
            corrected_text = issue.get('corrected_text', '')
            if corrected_text:
                sugg_color = self.COLOR_SUGGESTION.hexval()[2:8]
                elements.append(Paragraph(
                    f"<font color='#{sugg_color}'>参考修改: {corrected_text}</font>",
                    self.styles['ChineseSmall']
                ))

        # Separator line
        elements.append(Spacer(1, 0.2*cm))
        line_table = Table([['']], colWidths=[17*cm])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, self.COLOR_BORDER),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.3*cm))

        return elements

    def _add_footer(self, story: List, report_data: Dict[str, Any]):
        """Add report footer"""
        story.append(Spacer(1, 1*cm))

        # Check status
        status = report_data.get('status', '')
        status_text = {'completed': '检查完成', 'processing': '检查中', 'failed': '检查失败'}.get(status, status)

        footer_style = ParagraphStyle(
            name='Footer',
            fontName=self.font_name,
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.gray,
        )

        story.append(Paragraph(f"状态: {status_text}", footer_style))
        story.append(Paragraph("本报告由山东财经大学计算机与人工智能学院论文检查系统自动生成", footer_style))

    def _format_datetime(self, datetime_str: str) -> str:
        """Format datetime string for display"""
        if not datetime_str:
            return ''
        try:
            # Try to parse ISO format
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return datetime_str


def generate_pdf_report(report_data: Dict[str, Any], fonts_dir: str = None) -> bytes:
    """
    Generate PDF report from report data

    Args:
        report_data: Report data dictionary
        fonts_dir: Directory containing font files (optional)

    Returns:
        PDF file as bytes
    """
    generator = PDFReportGenerator(fonts_dir=fonts_dir)
    return generator.generate_report(report_data)
