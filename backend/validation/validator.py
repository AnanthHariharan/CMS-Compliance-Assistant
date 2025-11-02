"""
Note Validation Module
Combines rule-based and LLM-based validation
"""

from typing import List, Dict
from backend.validation.rules import ComplianceRules
from backend.llm.chains import LLMChain
from backend.retrieval.search import SemanticSearch


class NoteValidator:
    """Validates visit notes for CMS compliance"""

    def __init__(
        self,
        search_engine: SemanticSearch,
        llm_chain: LLMChain,
        use_rules: bool = True
    ):
        """
        Initialize note validator

        Args:
            search_engine: SemanticSearch instance
            llm_chain: LLMChain instance
            use_rules: Whether to use rule-based validation
        """
        self.search_engine = search_engine
        self.llm_chain = llm_chain
        self.use_rules = use_rules

        if use_rules:
            self.rules = ComplianceRules()

    def validate(self, note_text: str, n_guidelines: int = 7) -> Dict[str, any]:
        """
        Validate visit note

        Args:
            note_text: Visit note text
            n_guidelines: Number of relevant guidelines to retrieve

        Returns:
            Validation result
        """
        # Step 1: Rule-based validation
        rule_violations = []
        if self.use_rules:
            rule_violations = self.rules.validate_note(note_text)

        # Step 2: Retrieve relevant guidelines
        # Create a search query from the note
        search_query = self._create_search_query(note_text)
        guidelines = self.search_engine.search(
            query=search_query,
            n_results=n_guidelines
        )

        # Step 3: LLM-based validation
        llm_result = self.llm_chain.validate_note(note_text, guidelines)

        # Step 4: Combine results
        combined_result = self._combine_results(rule_violations, llm_result, guidelines)

        return combined_result

    def _create_search_query(self, note_text: str) -> str:
        """
        Create search query from note text

        Args:
            note_text: Visit note text

        Returns:
            Search query
        """
        # Extract key concepts for searching guidelines
        keywords = []

        if 'skilled nursing' in note_text.lower():
            keywords.append('skilled nursing services')

        if 'wound' in note_text.lower():
            keywords.append('wound care')

        if 'physical therapy' in note_text.lower() or 'pt ' in note_text.lower():
            keywords.append('physical therapy')

        if 'occupational therapy' in note_text.lower() or 'ot ' in note_text.lower():
            keywords.append('occupational therapy')

        # Default query
        if not keywords:
            keywords = ['home health services', 'documentation requirements', 'visit notes']

        return ' '.join(keywords) + ' requirements medical necessity homebound'

    def _combine_results(
        self,
        rule_violations: List[Dict[str, str]],
        llm_result: Dict[str, any],
        guidelines: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Combine rule-based and LLM-based results

        Args:
            rule_violations: Violations from rules
            llm_result: Result from LLM validation
            guidelines: Retrieved guidelines

        Returns:
            Combined validation result
        """
        # Combine violations
        all_violations = rule_violations.copy()

        # Add LLM violations if they're different
        llm_violations = llm_result.get('violations', [])
        for llm_v in llm_violations:
            # Check if similar violation already exists
            is_duplicate = any(
                v.get('category') == llm_v.get('category')
                for v in all_violations
            )
            if not is_duplicate:
                all_violations.append(llm_v)

        # Calculate overall score
        critical_count = sum(1 for v in all_violations if v.get('severity') == 'critical')
        major_count = sum(1 for v in all_violations if v.get('severity') == 'major')
        minor_count = sum(1 for v in all_violations if v.get('severity') == 'minor')

        # Scoring: Start at 100, deduct points
        score = 100.0
        score -= critical_count * 30
        score -= major_count * 15
        score -= minor_count * 5
        score = max(0, score)

        # Determine status
        if critical_count > 0 or score < 60:
            status = 'non_compliant'
        elif major_count > 2 or score < 80:
            status = 'needs_review'
        else:
            status = 'compliant'

        # Get strengths from LLM result
        strengths = llm_result.get('strengths', [])

        # If no violations found, note good documentation
        if not all_violations:
            strengths.append("All required elements are present")
            strengths.append("Documentation meets CMS guidelines")

        # Create summary
        summary = self._create_summary(status, score, all_violations, strengths)

        return {
            'status': status,
            'overall_score': score,
            'violations': all_violations,
            'strengths': strengths,
            'summary': summary,
            'guideline_references': [
                {
                    'text': g['text'][:200] + '...',
                    'page_number': g['page_number'],
                    'section_header': g['section_header']
                }
                for g in guidelines[:3]  # Top 3 relevant guidelines
            ]
        }

    def _create_summary(
        self,
        status: str,
        score: float,
        violations: List[Dict[str, str]],
        strengths: List[str]
    ) -> str:
        """
        Create summary text

        Args:
            status: Compliance status
            score: Overall score
            violations: List of violations
            strengths: List of strengths

        Returns:
            Summary text
        """
        summary_parts = []

        # Status statement
        if status == 'compliant':
            summary_parts.append(f"This visit note is COMPLIANT with CMS guidelines (Score: {score:.1f}/100).")
        elif status == 'needs_review':
            summary_parts.append(f"This visit note NEEDS REVIEW (Score: {score:.1f}/100).")
        else:
            summary_parts.append(f"This visit note is NON-COMPLIANT with CMS guidelines (Score: {score:.1f}/100).")

        # Violations summary
        if violations:
            critical = sum(1 for v in violations if v.get('severity') == 'critical')
            major = sum(1 for v in violations if v.get('severity') == 'major')
            minor = sum(1 for v in violations if v.get('severity') == 'minor')

            viol_text = f"Found {len(violations)} issue(s): "
            parts = []
            if critical > 0:
                parts.append(f"{critical} critical")
            if major > 0:
                parts.append(f"{major} major")
            if minor > 0:
                parts.append(f"{minor} minor")

            summary_parts.append(viol_text + ", ".join(parts) + ".")

        # Strengths
        if strengths:
            summary_parts.append(f"Strengths: {len(strengths)} well-documented aspect(s).")

        return " ".join(summary_parts)


def create_validator(
    search_engine: SemanticSearch,
    llm_chain: LLMChain,
    use_rules: bool = True
) -> NoteValidator:
    """
    Create validator instance

    Args:
        search_engine: SemanticSearch instance
        llm_chain: LLMChain instance
        use_rules: Use rule-based validation

    Returns:
        NoteValidator instance
    """
    return NoteValidator(
        search_engine=search_engine,
        llm_chain=llm_chain,
        use_rules=use_rules
    )
