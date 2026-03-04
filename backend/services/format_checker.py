"""
Format checker for thesis documents
Checks formatting according to Shandong University of Finance and Economics rules
"""
from typing import List, Dict, Any
from services.doc_parser import DocParser, ParagraphInfo
from models.check_rules import FormatIssue, IssueCategory, FORMAT_CHECK_RULES
from config import Config
import re


class FormatChecker:
    """Format checker for thesis documents"""

    def __init__(self, doc_parser: DocParser):
        self.doc_parser = doc_parser
        self.issues: List[FormatIssue] = []
        self.rules = Config.FORMAT_RULES

    def check_all(self) -> List[FormatIssue]:
        """Run all format checks"""
        self.issues = []

        self.check_page_setup()
        self.check_chapter_titles()
        self.check_section_titles()
        self.check_subsection_titles()
        self.check_body_text()
        self.check_abstract()
        self.check_references()
        self.check_figures_and_tables()

        return self.issues

    def check_page_setup(self):
        """Check page setup (margins, paper size)"""
        if not self.doc_parser.page_settings:
            return

        settings = self.doc_parser.page_settings
        expected = self.rules['page']

        # Check margins
        if abs(settings.margin_top - expected['margin_top']) > 0.2:
            self.issues.append(FormatIssue(
                type="error",
                category=IssueCategory.PAGE_SETUP.value,
                location="页面设置",
                message=f"上边距不符合要求，当前: {settings.margin_top:.1f}cm",
                suggestion=f"请将上边距设置为 {expected['margin_top']}cm",
                details={'current': settings.margin_top, 'expected': expected['margin_top']}
            ))

        if abs(settings.margin_bottom - expected['margin_bottom']) > 0.2:
            self.issues.append(FormatIssue(
                type="error",
                category=IssueCategory.PAGE_SETUP.value,
                location="页面设置",
                message=f"下边距不符合要求，当前: {settings.margin_bottom:.1f}cm",
                suggestion=f"请将下边距设置为 {expected['margin_bottom']}cm",
                details={'current': settings.margin_bottom, 'expected': expected['margin_bottom']}
            ))

        if abs(settings.margin_left - expected['margin_inner']) > 0.2:
            self.issues.append(FormatIssue(
                type="error",
                category=IssueCategory.PAGE_SETUP.value,
                location="页面设置",
                message=f"左边距不符合要求，当前: {settings.margin_left:.1f}cm",
                suggestion=f"请将左边距设置为 {expected['margin_inner']}cm",
                details={'current': settings.margin_left, 'expected': expected['margin_inner']}
            ))

        if abs(settings.margin_right - expected['margin_outer']) > 0.2:
            self.issues.append(FormatIssue(
                type="error",
                category=IssueCategory.PAGE_SETUP.value,
                location="页面设置",
                message=f"右边距不符合要求，当前: {settings.margin_right:.1f}cm",
                suggestion=f"请将右边距设置为 {expected['margin_outer']}cm",
                details={'current': settings.margin_right, 'expected': expected['margin_outer']}
            ))

    def check_chapter_titles(self):
        """Check chapter title formatting"""
        if not self.doc_parser.structure:
            return

        expected = self.rules['chapter_title']

        for chapter in self.doc_parser.structure.chapters:
            title = chapter.get('title', '')
            location = f"章节: {title[:30]}..." if len(title) > 30 else f"章节: {title}"

            # Check font size
            font_size = chapter.get('font_size', 0)
            if abs(font_size - expected['font_size']) > 1:
                self.issues.append(FormatIssue(
                    type="error",
                    category=IssueCategory.CHAPTER_TITLE.value,
                    location=location,
                    message=f"章标题字号不正确，当前: {font_size:.1f}pt",
                    suggestion=f"请将章标题字号设置为 {expected['font_size']}pt（三号）",
                    details={'current': font_size, 'expected': expected['font_size']}
                ))

            # Check font name
            font_name = chapter.get('font_name', '')
            if expected['font_name'] not in font_name:
                self.issues.append(FormatIssue(
                    type="error",
                    category=IssueCategory.CHAPTER_TITLE.value,
                    location=location,
                    message=f"章标题字体不正确，当前: {font_name}",
                    suggestion=f"请将章标题字体设置为 {expected['font_name']}",
                    details={'current': font_name, 'expected': expected['font_name']}
                ))

            # Check bold
            if not chapter.get('bold', False):
                self.issues.append(FormatIssue(
                    type="error",
                    category=IssueCategory.CHAPTER_TITLE.value,
                    location=location,
                    message="章标题未加粗",
                    suggestion="请将章标题设置为加粗",
                    details={'current': '未加粗', 'expected': '加粗'}
                ))

            # Check alignment
            alignment = chapter.get('alignment', 'left')
            if alignment != expected['alignment']:
                self.issues.append(FormatIssue(
                    type="error",
                    category=IssueCategory.CHAPTER_TITLE.value,
                    location=location,
                    message=f"章标题对齐方式不正确，当前: {alignment}",
                    suggestion="请将章标题设置为居中对齐",
                    details={'current': alignment, 'expected': expected['alignment']}
                ))

    def check_section_titles(self):
        """Check section title formatting"""
        if not self.doc_parser.structure:
            return

        expected = self.rules['section_title']

        for chapter in self.doc_parser.structure.chapters:
            for section in chapter.get('sections', []):
                title = section.get('title', '')
                location = f"节标题: {title[:30]}..." if len(title) > 30 else f"节标题: {title}"

                # Check font size
                font_size = section.get('font_size', 0)
                if abs(font_size - expected['font_size']) > 1:
                    self.issues.append(FormatIssue(
                        type="error",
                        category=IssueCategory.SECTION_TITLE.value,
                        location=location,
                        message=f"节标题字号不正确，当前: {font_size:.1f}pt",
                        suggestion=f"请将节标题字号设置为 {expected['font_size']}pt（四号）",
                        details={'current': font_size, 'expected': expected['font_size']}
                    ))

                # Check font name
                font_name = section.get('font_name', '')
                if expected['font_name'] not in font_name:
                    self.issues.append(FormatIssue(
                        type="warning",
                        category=IssueCategory.SECTION_TITLE.value,
                        location=location,
                        message=f"节标题字体可能不正确，当前: {font_name}",
                        suggestion=f"建议将节标题字体设置为 {expected['font_name']}",
                        details={'current': font_name, 'expected': expected['font_name']}
                    ))

                # Check bold
                if not section.get('bold', False):
                    self.issues.append(FormatIssue(
                        type="error",
                        category=IssueCategory.SECTION_TITLE.value,
                        location=location,
                        message="节标题未加粗",
                        suggestion="请将节标题设置为加粗",
                        details={'current': '未加粗', 'expected': '加粗'}
                    ))

    def check_subsection_titles(self):
        """Check subsection title formatting"""
        if not self.doc_parser.structure:
            return

        expected = self.rules['subsection_title']

        for chapter in self.doc_parser.structure.chapters:
            for section in chapter.get('sections', []):
                for subsection in section.get('subsections', []):
                    title = subsection.get('title', '')
                    location = f"小节标题: {title[:30]}..." if len(title) > 30 else f"小节标题: {title}"

                    # Check font size
                    font_size = subsection.get('font_size', 0)
                    if abs(font_size - expected['font_size']) > 0.5:
                        self.issues.append(FormatIssue(
                            type="error",
                            category=IssueCategory.SUBSECTION_TITLE.value,
                            location=location,
                            message=f"小节标题字号不正确，当前: {font_size:.1f}pt",
                            suggestion=f"请将小节标题字号设置为 {expected['font_size']}pt（小四）",
                            details={'current': font_size, 'expected': expected['font_size']}
                        ))

                    # Check font name
                    font_name = subsection.get('font_name', '')
                    if expected['font_name'] not in font_name:
                        self.issues.append(FormatIssue(
                            type="warning",
                            category=IssueCategory.SUBSECTION_TITLE.value,
                            location=location,
                            message=f"小节标题字体可能不正确，当前: {font_name}",
                            suggestion=f"建议将小节标题字体设置为 {expected['font_name']}",
                            details={'current': font_name, 'expected': expected['font_name']}
                        ))

                    # Check first line indent
                    first_indent = subsection.get('first_line_indent', 0)
                    expected_indent_cm = 0.74  # Approximately 2 characters (0.74cm)
                    if first_indent < 0.5:
                        self.issues.append(FormatIssue(
                            type="error",
                            category=IssueCategory.SUBSECTION_TITLE.value,
                            location=location,
                            message="小节标题首行未缩进",
                            suggestion="请将小节标题首行缩进2字符",
                            details={'current': first_indent, 'expected': expected_indent_cm}
                        ))

    def check_body_text(self):
        """Check body text formatting"""
        if not self.doc_parser.paragraphs:
            return

        expected = self.rules['body_text']
        sample_size = min(50, len(self.doc_parser.paragraphs))  # Check first 50 paragraphs

        for i, para in enumerate(self.doc_parser.paragraphs[:sample_size]):
            # Skip titles and short paragraphs
            if len(para.text) < 50:
                continue

            # Skip if it looks like a title (starts with chapter/section numbers)
            if re.match(r'^(第[一二三四五六七八九十\d]+章|\d+\.\d+)', para.text):
                continue

            location = f"正文第{i+1}段"

            # Check font size
            if abs(para.font_size_pt - expected['font_size']) > 1:
                self.issues.append(FormatIssue(
                    type="error",
                    category=IssueCategory.BODY_TEXT.value,
                    location=location,
                    message=f"正文字号不正确，当前: {para.font_size_pt:.1f}pt",
                    suggestion=f"请将正文字号设置为 {expected['font_size']}pt（小四）",
                    details={'current': para.font_size_pt, 'expected': expected['font_size']}
                ))

            # Check first line indent
            expected_indent_cm = 0.74  # 2 characters
            if para.first_line_indent < 0.5:
                self.issues.append(FormatIssue(
                    type="error",
                    category=IssueCategory.BODY_TEXT.value,
                    location=location,
                    message="正文首行未缩进或缩进不足",
                    suggestion="请将正文首行缩进2字符",
                    details={'current': para.first_line_indent, 'expected': expected_indent_cm}
                ))

            # Check line spacing (approximately)
            if para.line_spacing < 1.3 or para.line_spacing > 1.7:
                if para.line_spacing != 1.0:  # Sometimes line_spacing is 1.0 (single) by default
                    self.issues.append(FormatIssue(
                        type="warning",
                        category=IssueCategory.BODY_TEXT.value,
                        location=location,
                        message=f"正文行距可能不正确，当前: {para.line_spacing:.1f}",
                        suggestion="请将正文行距设置为1.5倍行距",
                        details={'current': para.line_spacing, 'expected': expected['line_spacing']}
                    ))

            # Only check a few body paragraphs to avoid too many duplicate issues
            break

    def check_abstract(self):
        """Check abstract formatting and content"""
        if not self.doc_parser.structure:
            return

        expected = self.rules['abstract']
        structure = self.doc_parser.structure

        # Check Chinese abstract
        if structure.abstract_cn:
            cn_length = len(structure.abstract_cn)
            if cn_length < expected['min_length']:
                self.issues.append(FormatIssue(
                    type="error",
                    category=IssueCategory.ABSTRACT.value,
                    location="中文摘要",
                    message=f"中文摘要字数不足，当前: {cn_length}字",
                    suggestion=f"请将中文摘要扩充至{expected['min_length']}-{expected['max_length']}字",
                    details={'current': cn_length, 'expected_min': expected['min_length']}
                ))
            elif cn_length > expected['max_length']:
                self.issues.append(FormatIssue(
                    type="warning",
                    category=IssueCategory.ABSTRACT.value,
                    location="中文摘要",
                    message=f"中文摘要字数过多，当前: {cn_length}字",
                    suggestion=f"请将中文摘要精简至{expected['max_length']}字以内",
                    details={'current': cn_length, 'expected_max': expected['max_length']}
                ))
        else:
            self.issues.append(FormatIssue(
                type="error",
                category=IssueCategory.ABSTRACT.value,
                location="中文摘要",
                message="未检测到中文摘要",
                suggestion="请添加中文摘要",
                details={}
            ))

        # Check English abstract
        if not structure.abstract_en:
            self.issues.append(FormatIssue(
                type="warning",
                category=IssueCategory.ABSTRACT.value,
                location="英文摘要",
                message="未检测到英文摘要",
                suggestion="请添加英文摘要(Abstract)",
                details={}
            ))

    def check_references(self):
        """Check references formatting and count"""
        if not self.doc_parser.structure:
            return

        expected = self.rules['references']
        references = self.doc_parser.structure.references

        # Check reference count
        ref_count = len(references)
        if ref_count < expected['min_count']:
            self.issues.append(FormatIssue(
                type="error",
                category=IssueCategory.REFERENCE.value,
                location="参考文献",
                message=f"参考文献数量不足，当前: {ref_count}篇",
                suggestion=f"请至少添加{expected['min_count']}篇参考文献",
                details={'current': ref_count, 'expected_min': expected['min_count']}
            ))

        # Check reference format (basic GB/T 7714 check)
        for i, ref in enumerate(references[:20]):  # Check first 20
            # Check for standard reference format markers
            if not re.search(r'\[J\]|\[M\]|\[D\]|\[C\]|\[N\]|\[R\]|\[S\]|\[EB/OL\]', ref):
                self.issues.append(FormatIssue(
                    type="warning",
                    category=IssueCategory.REFERENCE.value,
                    location=f"参考文献[{i+1}]",
                    message="参考文献格式可能不正确，缺少文献类型标识",
                    suggestion="请按照GB/T 7714规范添加文献类型标识，如[J]期刊、[M]专著等",
                    details={'reference': ref[:50]}
                ))

        # Check for recent references (years 2022-2025)
        current_year = 2025
        recent_count = 0
        for ref in references:
            years = re.findall(r'(20\d{2})', ref)
            if years:
                year = int(years[-1])  # Take the last year found
                if current_year - year <= 3:
                    recent_count += 1

        if ref_count > 0:
            recent_ratio = recent_count / ref_count
            if recent_ratio < expected['recent_years_ratio']:
                self.issues.append(FormatIssue(
                    type="warning",
                    category=IssueCategory.REFERENCE.value,
                    location="参考文献",
                    message=f"近三年参考文献比例不足，当前: {recent_ratio*100:.1f}%",
                    suggestion=f"请增加近三年（2022-2025）的参考文献，比例应不低于{expected['recent_years_ratio']*100:.0f}%",
                    details={'current_ratio': recent_ratio, 'expected_ratio': expected['recent_years_ratio']}
                ))

    def check_figures_and_tables(self):
        """Check figure and table formatting"""
        # Check for figure/table captions in document
        full_text = self.doc_parser.get_full_text()

        # Look for potential figure captions
        figure_patterns = [
            r'图\s*\d+[\.\s]',
            r'图\d+[-\s]',
        ]

        # Look for potential table captions
        table_patterns = [
            r'表\s*\d+[\.\s]',
            r'表\d+[-\s]',
        ]

        figures_found = []
        tables_found = []

        for pattern in figure_patterns:
            figures_found.extend(re.findall(pattern, full_text))

        for pattern in table_patterns:
            tables_found.extend(re.findall(pattern, full_text))

        # Check if figure numbering follows chapter pattern
        if figures_found:
            # Check for proper chapter-based numbering (e.g., 图1-1, 图2-1)
            chapter_based = any(re.match(r'图\s*\d+[-\.]', f) for f in figures_found)
            if not chapter_based:
                self.issues.append(FormatIssue(
                    type="suggestion",
                    category=IssueCategory.FIGURE_TABLE.value,
                    location="图表编号",
                    message="图表编号建议按章编号",
                    suggestion='建议采用"按章编号"格式，如"图1-1"、"图2-1"等',
                    details={}
                ))
