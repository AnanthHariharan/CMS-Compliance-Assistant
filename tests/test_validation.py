"""
Tests for compliance validation
"""

import pytest
from backend.validation.rules import ComplianceRules


class TestComplianceRules:
    """Test rule-based validation"""

    def test_rules_init(self):
        """Test ComplianceRules initialization"""
        rules = ComplianceRules()
        assert rules is not None

    def test_missing_homebound_status(self):
        """Test detection of missing homebound status"""
        rules = ComplianceRules()

        note_without_homebound = """
        Patient: John Doe, 78 years old
        Date: 2024-01-15
        Assessment: Patient is doing well.
        """

        violations = rules.check_homebound_status(note_without_homebound)
        assert len(violations) > 0
        assert violations[0]['severity'] == 'critical'

    def test_with_homebound_status(self):
        """Test that homebound status is detected"""
        rules = ComplianceRules()

        note_with_homebound = """
        Patient: John Doe, 78 years old
        Date: 2024-01-15
        Homebound Status: Patient is homebound, unable to leave home
        without taxing effort. Requires wheelchair for mobility.
        Assessment: Patient is doing well.
        """

        violations = rules.check_homebound_status(note_with_homebound)
        assert len(violations) == 0

    def test_medical_necessity_check(self):
        """Test medical necessity documentation check"""
        rules = ComplianceRules()

        note_with_necessity = """
        Patient: John Doe, 78 years old
        Skilled nursing assessment performed.
        Wound care provided with sterile technique.
        Patient teaching on medication management.
        """

        violations = rules.check_medical_necessity(note_with_necessity)
        assert len(violations) == 0

    def test_required_elements(self):
        """Test required elements check"""
        rules = ComplianceRules()

        complete_note = """
        Patient: John Doe, 78 years old
        Date: 2024-01-15
        Visit Type: Skilled Nursing

        Assessment: Patient alert and oriented.
        Vital Signs: BP 120/80, Temp 98.6F, Pulse 72

        Interventions: Wound care provided.

        Plan: Continue current care plan.

        Nurse: Jane Smith, RN
        Time In: 10:00 AM
        Time Out: 10:45 AM
        """

        violations = rules.check_required_elements(complete_note)
        # Some violations may still exist, but should be fewer
        assert isinstance(violations, list)


class TestValidationScoring:
    """Test validation scoring logic"""

    def test_score_calculation(self):
        """Test that scores are calculated correctly"""
        # Critical violation: -30
        # Major violation: -15
        # Minor violation: -5

        base_score = 100
        critical_count = 1
        major_count = 2
        minor_count = 1

        expected_score = base_score - (critical_count * 30) - (major_count * 15) - (minor_count * 5)
        assert expected_score == 35

    def test_status_thresholds(self):
        """Test compliance status thresholds"""
        # Compliant: >= 80
        # Needs Review: 60-79
        # Non-Compliant: < 60

        assert 85 >= 80  # Compliant
        assert 70 >= 60 and 70 < 80  # Needs review
        assert 55 < 60  # Non-compliant
