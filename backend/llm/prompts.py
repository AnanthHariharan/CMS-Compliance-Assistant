"""
Prompt Templates
Templates for LLM prompts
"""


QA_SYSTEM_PROMPT = """You are a CMS (Centers for Medicare & Medicaid Services) compliance expert specializing in home health care regulations. Your role is to provide accurate, helpful information about Medicare guidelines based on the provided context.

Guidelines:
- Answer questions based ONLY on the provided context from CMS guidelines
- If the answer is not in the context, clearly state that you don't have enough information
- Cite specific sections or requirements when possible
- Be precise and professional in your responses
- Use clear, accessible language while maintaining accuracy
- If relevant, mention page numbers from the source documents
"""


QA_USER_PROMPT = """Based on the following context from CMS Medicare guidelines, please answer the question.

CONTEXT:
{context}

QUESTION: {question}

Please provide a clear, accurate answer based on the context above. If the context doesn't contain enough information to fully answer the question, please state that clearly."""


VALIDATION_SYSTEM_PROMPT = """You are a CMS compliance auditor specializing in home health care documentation. Your role is to review visit notes and identify compliance issues according to Medicare regulations.

Your task:
1. Analyze the visit note for compliance with CMS requirements
2. Identify specific violations or missing required elements
3. Categorize violations by severity (critical, major, minor)
4. Provide actionable recommendations for each violation
5. Cite relevant CMS guidelines when possible

Be thorough, objective, and constructive in your feedback."""


VALIDATION_USER_PROMPT = """Review the following home health visit note for CMS compliance.

VISIT NOTE:
{note_text}

RELEVANT CMS GUIDELINES:
{guidelines}

Please analyze this visit note and identify:
1. All compliance violations or missing required elements
2. The severity of each violation (critical, major, minor)
3. Specific recommendations to fix each violation
4. References to relevant CMS guidelines

Also note any strengths in the documentation.

Provide your analysis in a structured format."""


COMPLIANCE_CATEGORIES = {
    "homebound_status": "Homebound Status Documentation",
    "medical_necessity": "Medical Necessity",
    "physician_orders": "Physician Orders and Plan of Care",
    "skilled_service": "Skilled Service Documentation",
    "patient_assessment": "Patient Assessment",
    "interventions": "Interventions and Treatment",
    "patient_progress": "Patient Progress Documentation",
    "visit_details": "Visit Details and Timing",
    "safety_assessment": "Safety Assessment",
    "signature_certification": "Signature and Certification"
}


def format_qa_prompt(question: str, context_chunks: list) -> tuple[str, str]:
    """
    Format Q&A prompt with context

    Args:
        question: User question
        context_chunks: List of context chunks

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Format context
    context_text = "\n\n---\n\n".join([
        f"[Source: Page {chunk.get('page_number', 'N/A')}]\n{chunk['text']}"
        for chunk in context_chunks
    ])

    user_prompt = QA_USER_PROMPT.format(
        context=context_text,
        question=question
    )

    return QA_SYSTEM_PROMPT, user_prompt


def format_validation_prompt(note_text: str, guidelines: list) -> tuple[str, str]:
    """
    Format validation prompt with guidelines

    Args:
        note_text: Visit note text
        guidelines: Relevant guideline chunks

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Format guidelines
    guidelines_text = "\n\n---\n\n".join([
        f"[Section: {chunk.get('section_header', 'General')} - Page {chunk.get('page_number', 'N/A')}]\n{chunk['text']}"
        for chunk in guidelines
    ])

    user_prompt = VALIDATION_USER_PROMPT.format(
        note_text=note_text,
        guidelines=guidelines_text
    )

    return VALIDATION_SYSTEM_PROMPT, user_prompt
