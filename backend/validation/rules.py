"""
Compliance Rules
Rule-based validation for CMS requirements
"""

import re
from typing import List, Dict


class ComplianceRules:
    """Rule-based compliance checker"""

    # Required elements for home health visit notes
    REQUIRED_ELEMENTS = {
        'patient_info': ['patient', 'name', 'age', 'dob'],
        'visit_date': ['date'],
        'visit_type': ['visit type', 'skilled nursing', 'physical therapy', 'occupational therapy'],
        'assessment': ['assessment', 'evaluation', 'status'],
        'interventions': ['intervention', 'treatment', 'care provided'],
        'vital_signs': ['vital signs', 'bp', 'blood pressure', 'temperature', 'pulse', 'heart rate'],
        'plan': ['plan', 'plan of care', 'continuing'],
        'nurse_signature': ['rn', 'nurse', 'signature', 'signed'],
        'time_in_out': ['time in', 'time out', 'arrival', 'departure']
    }

    # Critical keywords for homebound status
    HOMEBOUND_KEYWORDS = [
        'homebound',
        'unable to leave home',
        'confined to home',
        'wheelchair bound',
        'walker',
        'assistance to leave',
        'taxing effort'
    ]

    # Medical necessity indicators
    MEDICAL_NECESSITY_KEYWORDS = [
        'skilled',
        'assessment',
        'evaluation',
        'teaching',
        'monitoring',
        'wound care',
        'medication management',
        'observation'
    ]

    def __init__(self):
        """Initialize compliance rules"""
        pass

    def check_required_elements(self, note_text: str) -> List[Dict[str, str]]:
        """
        Check for required elements in note

        Args:
            note_text: Visit note text

        Returns:
            List of missing element violations
        """
        violations = []
        note_lower = note_text.lower()

        for element_type, keywords in self.REQUIRED_ELEMENTS.items():
            # Check if any keyword is present
            found = any(keyword in note_lower for keyword in keywords)

            if not found:
                violations.append({
                    'category': element_type,
                    'severity': 'major' if element_type in ['assessment', 'interventions', 'plan'] else 'minor',
                    'description': f"Missing required element: {element_type.replace('_', ' ').title()}",
                    'recommendation': f"Include {element_type.replace('_', ' ')} in the visit note",
                    'guideline_reference': 'CMS Medicare Benefit Policy Manual'
                })

        return violations

    def check_homebound_status(self, note_text: str) -> List[Dict[str, str]]:
        """
        Check for homebound status documentation

        Args:
            note_text: Visit note text

        Returns:
            List of violations
        """
        violations = []
        note_lower = note_text.lower()

        # Check if any homebound indicator is present
        has_homebound = any(keyword in note_lower for keyword in self.HOMEBOUND_KEYWORDS)

        if not has_homebound:
            violations.append({
                'category': 'homebound_status',
                'severity': 'critical',
                'description': "Missing homebound status documentation",
                'recommendation': "Document patient's homebound status, including why patient cannot leave home or requires taxing effort to leave",
                'guideline_reference': 'Section 30.1.1 - Homebound Requirement'
            })

        return violations

    def check_medical_necessity(self, note_text: str) -> List[Dict[str, str]]:
        """
        Check for medical necessity documentation

        Args:
            note_text: Visit note text

        Returns:
            List of violations
        """
        violations = []
        note_lower = note_text.lower()

        # Count medical necessity indicators
        necessity_count = sum(1 for keyword in self.MEDICAL_NECESSITY_KEYWORDS if keyword in note_lower)

        if necessity_count < 2:
            violations.append({
                'category': 'medical_necessity',
                'severity': 'critical',
                'description': "Insufficient medical necessity documentation",
                'recommendation': "Clearly document skilled nursing services provided and why they are medically necessary",
                'guideline_reference': 'Section 40 - Covered Services'
            })

        return violations

    def check_visit_duration(self, note_text: str) -> List[Dict[str, str]]:
        """
        Check if visit duration is documented and reasonable

        Args:
            note_text: Visit note text

        Returns:
            List of violations
        """
        violations = []

        # Extract time in and time out
        time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)'
        times = re.findall(time_pattern, note_text)

        if len(times) < 2:
            violations.append({
                'category': 'visit_details',
                'severity': 'minor',
                'description': "Visit start and end times not clearly documented",
                'recommendation': "Document specific time in and time out for the visit",
                'guideline_reference': 'Documentation Requirements'
            })

        return violations

    def validate_note(self, note_text: str) -> List[Dict[str, str]]:
        """
        Run all rule-based validations

        Args:
            note_text: Visit note text

        Returns:
            List of all violations found
        """
        all_violations = []

        # Run all checks
        all_violations.extend(self.check_required_elements(note_text))
        all_violations.extend(self.check_homebound_status(note_text))
        all_violations.extend(self.check_medical_necessity(note_text))
        all_violations.extend(self.check_visit_duration(note_text))

        return all_violations
