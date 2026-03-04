"""
AI content checker using LLM APIs
Checks content quality, language expression, academic norms
"""
import json
import re
from typing import List, Dict, Any, Optional
from services.doc_parser import DocParser
from models.check_rules import AIIssue, CheckSummary, IssueCategory
from utils.llm_client import LLMClient


# References check prompt template
REFERENCES_CHECK_PROMPT = """你是一位学术论文参考文献审核专家。请对以下论文的参考文献列表进行详细检查：

检查项目：

1. 真实性验证（最重要）：
   - 文献标题、作者、期刊/出版社是否真实存在
   - 年份、卷期、页码信息是否合理
   - 作者姓名是否符合学术规范（注意识别虚构作者）
   - 期刊名称是否正确（注意识别虚假期刊）
   - 标记明显伪造、可疑或无法验证的文献

2. 正文引用匹配：
   - 参考文献列表中的文献是否在正文中有引用
   - 正文引用标识是否都能在参考文献列表中找到对应
   - 识别"ghost references"（参考文献列表中有但正文未引用的文献）
   - 识别"missing citations"（正文引用了但参考文献列表中缺失的）

3. 格式规范性（GB/T 7714-2015）：
   - 文献类型标识是否正确：[J]期刊、[M]专著、[D]学位论文、[C]会议、[N]报纸、[R]报告、[EB/OL]电子文献
   - 必填字段是否完整（作者、标题、期刊/出版社、年份等）
   - 标点符号使用是否正确
   - 格式是否符合标准

请特别注意识别以下可疑迹象：
- 作者姓名明显虚构（如连续多个文献有相似的人名模式）
- 期刊名称拼写错误或为掠夺性期刊
- 标题明显为AI生成（过于通用、不通顺）
- 页码范围不合理（如1-999）
- 年份与内容明显不符

参考文献列表：
{references}

正文引用标识：
{citations}

请按以下JSON格式返回检查结果：
{{
  "issues": [
    {{
      "type": "error|warning|suggestion",
      "category": "参考文献真实性|引用匹配|格式规范",
      "reference_index": 1,
      "reference_text": "文献条目原文",
      "issue_description": "问题描述",
      "suggestion": "修改建议"
    }}
  ],
  "statistics": {{
    "total_references": 15,
    "cited_references": 12,
    "uncited_references": 3,
    "suspicious_references": 2,
    "missing_citations": 0
  }},
  "overall_assessment": "对参考文献整体质量的简要评价"
}}

注意：
- 请只返回JSON格式的结果，不要添加其他说明文字
- 对于疑似伪造的文献，务必标记为error类型
- reference_index从1开始计数
- 如果某个类别没有问题，返回空issues数组
"""

# AI check prompt template
AI_CHECK_PROMPT = """你是一位资深的学术论文评审专家。请对以下本科毕业论文内容进行详细检查，重点关注：

1. 语言表达问题：
   - 语法错误、错别字
   - 用词不当、口语化表达
   - 语句不通顺、表达不清晰

2. 学术规范问题：
   - 学术术语使用是否准确
   - 论述是否严谨、客观
   - 逻辑是否清晰、连贯

3. 内容质量问题：
   - 摘要是否准确概括全文
   - 各章节内容是否充实
   - 结论是否与正文一致

4. 引用规范：
   - 引用格式是否正确
   - 引用内容是否与参考文献对应

请按以下JSON格式返回检查结果：
{
  "issues": [
    {
      "type": "error|warning|suggestion",
      "location": "具体位置（如：第3章第2节第2段）",
      "original_text": "原文片段（30字以内）",
      "issue_description": "问题描述",
      "suggestion": "修改建议",
      "corrected_text": "建议修改后的文本（可选）"
    }
  ],
  "summary": {
    "total_issues": 5,
    "error_count": 2,
    "warning_count": 2,
    "suggestion_count": 1,
    "overall_evaluation": "论文整体评价（100字以内）"
  }
}

注意：
- 请只返回JSON格式的结果，不要添加其他说明文字
- 如果某个类别没有问题，可以返回空数组
- location尽量具体到章节段落
- overall_evaluation请客观评价论文质量

论文内容：
{content}
"""

# Section check prompt for long documents - concise version for speed
SECTION_CHECK_PROMPT = """请简要检查论文章节，最多返回3个主要问题：

章节：{section_title}

内容：
{content}

返回JSON（无问题时issues为空数组）：
{{
  "issues": [
    {{
      "type": "error|warning|suggestion",
      "location": "位置",
      "original_text": "原文",
      "issue_description": "问题",
      "suggestion": "建议"
    }}
  ]
}}
"""


class AIChecker:
    """AI content checker"""

    def __init__(self, doc_parser: DocParser, llm_client: LLMClient):
        self.doc_parser = doc_parser
        self.llm_client = llm_client
        self.issues: List[AIIssue] = []
        self.summary: Optional[CheckSummary] = None

    def check_all(self, check_types: List[str] = None) -> Dict[str, Any]:
        """
        Run all AI checks

        Args:
            check_types: List of check types to perform ['language', 'content', 'citation']

        Returns:
            Dictionary with issues and summary
        """
        if check_types is None:
            check_types = ['language', 'content', 'citation']

        self.issues = []

        # Get document content
        full_text = self.doc_parser.get_full_text()

        # For long documents, check by sections
        if len(full_text) > 8000:
            self._check_by_sections(check_types)
        else:
            self._check_full_document(full_text, check_types)

        # Generate summary
        self._generate_summary()

        return {
            'issues': [issue.to_dict() for issue in self.issues],
            'summary': self.summary.to_dict() if self.summary else None
        }

    def _check_full_document(self, content: str, check_types: List[str]):
        """Check full document at once (for shorter documents)"""
        # Limit content length
        if len(content) > 6000:
            content = content[:6000] + "\n...[内容已截断]"

        prompt = AI_CHECK_PROMPT.format(content=content)

        try:
            messages = [
                {"role": "system", "content": "你是一位专业的学术论文评审专家。"},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.chat(messages, temperature=0.3, max_tokens=4096)

            # Parse JSON response
            result = self._parse_json_response(response)

            if result and 'issues' in result:
                for issue_data in result['issues']:
                    issue = AIIssue(
                        type=issue_data.get('type', 'suggestion'),
                        location=issue_data.get('location', '未知位置'),
                        original_text=issue_data.get('original_text', ''),
                        issue_description=issue_data.get('issue_description', ''),
                        suggestion=issue_data.get('suggestion', ''),
                        corrected_text=issue_data.get('corrected_text')
                    )
                    self.issues.append(issue)

            if result and 'summary' in result:
                summary_data = result['summary']
                self.summary = CheckSummary(
                    total_issues=summary_data.get('total_issues', 0),
                    error_count=summary_data.get('error_count', 0),
                    warning_count=summary_data.get('warning_count', 0),
                    suggestion_count=summary_data.get('suggestion_count', 0),
                    overall_evaluation=summary_data.get('overall_evaluation', '')
                )

        except Exception as e:
            # Add error issue
            self.issues.append(AIIssue(
                type="error",
                location="AI检查",
                original_text="",
                issue_description=f"AI检查过程中出现错误: {str(e)}",
                suggestion="请检查API配置或稍后重试"
            ))

    def _check_by_sections(self, check_types: List[str]):
        """Check document by sections (for longer documents)"""
        if not self.doc_parser.structure:
            return

        # Check abstract (limited length for speed)
        if self.doc_parser.structure.abstract_cn:
            abstract = self.doc_parser.structure.abstract_cn[:1000]  # Limit abstract length
            self._check_section("摘要", abstract, check_types)

        # Check each chapter (limit to first 4 chapters for speed)
        for i, chapter in enumerate(self.doc_parser.structure.chapters[:4]):
            chapter_title = chapter.get('title', f'第{i+1}章')
            chapter_content = self.doc_parser.get_chapter_content(i)

            # Truncate long chapters to 1500 chars for speed
            if len(chapter_content) > 1500:
                chapter_content = chapter_content[:1500] + "\n...[内容已截断]"

            self._check_section(chapter_title, chapter_content, check_types)

    def _check_section(self, section_title: str, content: str, check_types: List[str]):
        """Check a specific section"""
        if len(content) < 100:
            return

        prompt = SECTION_CHECK_PROMPT.format(
            section_title=section_title,
            content=content[:3000]  # Limit content
        )

        try:
            messages = [
                {"role": "system", "content": "你是一位专业的学术论文评审专家。"},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.chat(messages, temperature=0.3, max_tokens=2048)

            result = self._parse_json_response(response)

            if result and 'issues' in result:
                for issue_data in result['issues']:
                    issue = AIIssue(
                        type=issue_data.get('type', 'suggestion'),
                        location=f"{section_title} - {issue_data.get('location', '未知位置')}",
                        original_text=issue_data.get('original_text', ''),
                        issue_description=issue_data.get('issue_description', ''),
                        suggestion=issue_data.get('suggestion', ''),
                        corrected_text=issue_data.get('corrected_text')
                    )
                    self.issues.append(issue)

        except Exception as e:
            # Log the error but don't stop checking other sections
            print(f"AI check failed for section '{section_title}': {str(e)}")
            import traceback
            traceback.print_exc()

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from LLM response"""
        try:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Try to find JSON object directly
            json_match = re.search(r'\{[\s\S]*"issues"[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group(0))

            # Try to parse entire response as JSON
            return json.loads(response)

        except json.JSONDecodeError:
            return None

    def _generate_summary(self):
        """Generate summary from issues"""
        error_count = sum(1 for i in self.issues if i.type == 'error')
        warning_count = sum(1 for i in self.issues if i.type == 'warning')
        suggestion_count = sum(1 for i in self.issues if i.type == 'suggestion')

        total = len(self.issues)

        if total == 0:
            evaluation = "论文整体质量良好，未发现明显问题。"
        elif error_count > 5:
            evaluation = "论文存在较多语言表达和格式问题，建议仔细修改。"
        elif warning_count > 5:
            evaluation = "论文整体尚可，但有一些需要改进的地方。"
        else:
            evaluation = "论文质量较好，只有少量细节需要完善。"

        self.summary = CheckSummary(
            total_issues=total,
            error_count=error_count,
            warning_count=warning_count,
            suggestion_count=suggestion_count,
            overall_evaluation=evaluation
        )

    def check_references(self) -> List[AIIssue]:
        """
        Check references for authenticity, citation matching, and format compliance
        This is a specialized check for references section
        """
        if not self.doc_parser.structure:
            return []

        references = self.doc_parser.get_references_section()
        citations = self.doc_parser.extract_citations()

        if not references:
            return []

        # Prepare citations summary for the prompt
        citation_summary = {}
        for c in citations:
            num = c['reference_number']
            citation_summary[num] = citation_summary.get(num, 0) + 1

        citations_text = "\n".join([
            f"[{num}]: 被引用 {count} 次"
            for num, count in sorted(citation_summary.items())
        ]) if citation_summary else "未检测到正文引用"

        # Limit references length for the prompt
        refs_text = references[:4000] if len(references) > 4000 else references
        if len(references) > 4000:
            refs_text += "\n...[参考文献已截断]"

        prompt = REFERENCES_CHECK_PROMPT.format(
            references=refs_text,
            citations=citations_text
        )

        reference_issues = []

        try:
            messages = [
                {"role": "system", "content": "你是一位专业的学术论文参考文献审核专家，擅长识别虚假文献和格式问题。"},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.chat(messages, temperature=0.2, max_tokens=4096)
            result = self._parse_json_response(response)

            if result and 'issues' in result:
                for issue_data in result['issues']:
                    # Map category to appropriate IssueCategory
                    category_map = {
                        '参考文献真实性': IssueCategory.REFERENCE_AUTHORITY.value,
                        '引用匹配': IssueCategory.REFERENCE_CITATION.value,
                        '格式规范': IssueCategory.REFERENCE_FORMAT.value,
                    }
                    category = category_map.get(
                        issue_data.get('category', '格式规范'),
                        IssueCategory.REFERENCE_FORMAT.value
                    )

                    issue = AIIssue(
                        type=issue_data.get('type', 'suggestion'),
                        location=f"参考文献[{issue_data.get('reference_index', '?')}]",
                        original_text=issue_data.get('reference_text', '')[:100],
                        issue_description=issue_data.get('issue_description', ''),
                        suggestion=issue_data.get('suggestion', '')
                    )
                    # Set the category attribute
                    issue.category = category
                    reference_issues.append(issue)

        except Exception as e:
            print(f"References check failed: {str(e)}")
            import traceback
            traceback.print_exc()

        return reference_issues

    def check_all_with_references(self, check_types: List[str] = None) -> Dict[str, Any]:
        """
        Run all AI checks including specialized references check

        Args:
            check_types: List of check types to perform ['language', 'content', 'citation', 'references']

        Returns:
            Dictionary with issues and summary
        """
        if check_types is None:
            check_types = ['language', 'content', 'citation', 'references']

        self.issues = []

        # Get document content
        full_text = self.doc_parser.get_full_text()

        # For long documents, check by sections
        if len(full_text) > 8000:
            self._check_by_sections(check_types)
        else:
            self._check_full_document(full_text, check_types)

        # Special handling for references check
        if 'references' in check_types:
            ref_issues = self.check_references()
            self.issues.extend(ref_issues)

        # Generate summary
        self._generate_summary()

        return {
            'issues': [self._issue_to_dict(issue) for issue in self.issues],
            'summary': self.summary.to_dict() if self.summary else None
        }

    def _issue_to_dict(self, issue: AIIssue) -> Dict[str, Any]:
        """Convert AIIssue to dict, including category if present"""
        result = issue.to_dict()
        if hasattr(issue, 'category'):
            result['category'] = issue.category
        return result
