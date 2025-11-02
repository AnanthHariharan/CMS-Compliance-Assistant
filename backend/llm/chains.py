"""
LLM Chains
Handles LLM interactions for Q&A and validation
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
import json
from backend.llm.prompts import format_qa_prompt, format_validation_prompt


class LLMChain:
    """Handles LLM operations using OpenAI API"""

    def __init__(
        self,
        api_key: str = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_tokens: int = 1500
    ):
        """
        Initialize LLM chain

        Args:
            api_key: OpenAI API key
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, any]]
    ) -> str:
        """
        Generate answer to question using context

        Args:
            question: User question
            context_chunks: Retrieved context chunks

        Returns:
            Generated answer
        """
        system_prompt, user_prompt = format_qa_prompt(question, context_chunks)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            answer = response.choices[0].message.content
            return answer

        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"I apologize, but I encountered an error generating an answer: {str(e)}"

    def stream_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, any]]
    ):
        """
        Stream answer generation

        Args:
            question: User question
            context_chunks: Retrieved context chunks

        Yields:
            Answer chunks
        """
        system_prompt, user_prompt = format_qa_prompt(question, context_chunks)

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            print(f"Error streaming answer: {e}")
            yield f"Error: {str(e)}"

    def validate_note(
        self,
        note_text: str,
        guidelines: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Validate visit note against CMS guidelines

        Args:
            note_text: Visit note text
            guidelines: Relevant guideline chunks

        Returns:
            Validation result dictionary
        """
        system_prompt, user_prompt = format_validation_prompt(note_text, guidelines)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=2000  # More tokens for validation
            )

            validation_text = response.choices[0].message.content

            # Parse the validation response
            result = self._parse_validation_response(validation_text)
            return result

        except Exception as e:
            print(f"Error validating note: {e}")
            return {
                'status': 'error',
                'overall_score': 0,
                'violations': [],
                'strengths': [],
                'summary': f"Error during validation: {str(e)}"
            }

    def _parse_validation_response(self, validation_text: str) -> Dict[str, any]:
        """
        Parse validation response from LLM

        Args:
            validation_text: Raw validation text

        Returns:
            Structured validation result
        """
        # Try to extract structured information
        violations = []
        strengths = []

        # Simple parsing - could be enhanced with structured output
        lines = validation_text.split('\n')

        current_violation = None
        in_violations = False
        in_strengths = False

        for line in lines:
            line = line.strip()

            # Detect sections
            if 'violation' in line.lower() or 'issue' in line.lower():
                in_violations = True
                in_strengths = False
            elif 'strength' in line.lower() or 'well' in line.lower():
                in_strengths = True
                in_violations = False

            # Extract violations
            if in_violations and line and not line.startswith('#'):
                if any(sev in line.lower() for sev in ['critical', 'major', 'minor']):
                    severity = 'critical' if 'critical' in line.lower() else \
                              'major' if 'major' in line.lower() else 'minor'

                    violations.append({
                        'category': 'General',
                        'severity': severity,
                        'description': line,
                        'recommendation': '',
                        'guideline_reference': ''
                    })

            # Extract strengths
            if in_strengths and line and line.startswith('-'):
                strengths.append(line[1:].strip())

        # Determine overall status
        critical_count = sum(1 for v in violations if v['severity'] == 'critical')
        major_count = sum(1 for v in violations if v['severity'] == 'major')

        if critical_count > 0 or major_count > 2:
            status = 'non_compliant'
            score = max(0, 100 - (critical_count * 30 + major_count * 15 + len(violations) * 5))
        elif len(violations) > 0:
            status = 'needs_review'
            score = max(50, 100 - len(violations) * 10)
        else:
            status = 'compliant'
            score = 100

        return {
            'status': status,
            'overall_score': float(score),
            'violations': violations,
            'strengths': strengths,
            'summary': validation_text[:500]  # First 500 chars as summary
        }


def create_llm_chain(
    api_key: str = None,
    model: str = "gpt-4o-mini"
) -> LLMChain:
    """
    Create LLM chain instance

    Args:
        api_key: OpenAI API key
        model: Model to use

    Returns:
        LLMChain instance
    """
    return LLMChain(api_key=api_key, model=model)
