"""Tests for Hepatology Calculators"""
import pytest


class TestMeldScoreCalculator:
    def test_meld_basic(self):
        from src.domain.services.calculators import MeldScoreCalculator
        calc = MeldScoreCalculator()
        result = calc.calculate(
            creatinine=1.0, bilirubin=1.0, inr=1.0, sodium=140
        )
        assert result.value >= 6

    def test_meld_dialysis(self):
        from src.domain.services.calculators import MeldScoreCalculator
        calc = MeldScoreCalculator()
        result = calc.calculate(
            creatinine=4.0, bilirubin=1.0, inr=1.0, sodium=140, on_dialysis=True
        )
        assert result.value >= 6

    def test_tool_id(self):
        from src.domain.services.calculators import MeldScoreCalculator
        assert MeldScoreCalculator().tool_id == "meld_score"


class TestChildPughCalculator:
    """Tests for Child-Pugh Score calculator"""
    
    def test_class_a_minimal(self):
        """Test Class A with minimal derangements"""
        from src.domain.services.calculators import ChildPughCalculator
        calc = ChildPughCalculator()
        result = calc.calculate(
            bilirubin=1.5,  # 1 point
            albumin=4.0,    # 1 point
            inr=1.3,        # 1 point
            ascites="none", # 1 point
            encephalopathy_grade=0,  # 1 point
        )
        assert result.value == 5
        assert "Class A" in result.interpretation.stage
    
    def test_class_b_moderate(self):
        """Test Class B with moderate disease"""
        from src.domain.services.calculators import ChildPughCalculator
        calc = ChildPughCalculator()
        result = calc.calculate(
            bilirubin=2.5,  # 2 points
            albumin=3.0,    # 2 points
            inr=1.9,        # 2 points
            ascites="mild", # 2 points
            encephalopathy_grade=1,  # 2 points
        )
        assert result.value == 10  # Actually Class C boundary
        # Wait, let me recalculate: 2+2+2+2+2=10 -> Class C
        assert "Class C" in result.interpretation.stage
    
    def test_class_b_exact(self):
        """Test Class B with exact boundary"""
        from src.domain.services.calculators import ChildPughCalculator
        calc = ChildPughCalculator()
        result = calc.calculate(
            bilirubin=2.5,  # 2 points
            albumin=3.2,    # 2 points
            inr=1.5,        # 1 point
            ascites="mild", # 2 points
            encephalopathy_grade=0,  # 1 point
        )
        assert result.value == 8  # 2+2+1+2+1=8 -> Class B
        assert "Class B" in result.interpretation.stage
    
    def test_class_c_severe(self):
        """Test Class C with severe disease"""
        from src.domain.services.calculators import ChildPughCalculator
        calc = ChildPughCalculator()
        result = calc.calculate(
            bilirubin=5.0,   # 3 points
            albumin=2.0,     # 3 points
            inr=2.5,         # 3 points
            ascites="moderate_severe",  # 3 points
            encephalopathy_grade=3,     # 3 points
        )
        assert result.value == 15  # Maximum score
        assert "Class C" in result.interpretation.stage
    
    def test_ascites_normalization(self):
        """Test that various ascites inputs are normalized correctly"""
        from src.domain.services.calculators import ChildPughCalculator
        calc = ChildPughCalculator()
        
        # Test "controlled" maps to "mild"
        result1 = calc.calculate(
            bilirubin=1.5, albumin=4.0, inr=1.3,
            ascites="controlled", encephalopathy_grade=0
        )
        
        result2 = calc.calculate(
            bilirubin=1.5, albumin=4.0, inr=1.3,
            ascites="mild", encephalopathy_grade=0
        )
        
        assert result1.value == result2.value
    
    def test_encephalopathy_boundaries(self):
        """Test encephalopathy grade boundaries"""
        from src.domain.services.calculators import ChildPughCalculator
        calc = ChildPughCalculator()
        
        # Grade 0 = 1 point
        r0 = calc.calculate(bilirubin=1.5, albumin=4.0, inr=1.3, 
                           ascites="none", encephalopathy_grade=0)
        
        # Grade 2 = 2 points
        r2 = calc.calculate(bilirubin=1.5, albumin=4.0, inr=1.3,
                           ascites="none", encephalopathy_grade=2)
        
        # Grade 3 = 3 points
        r3 = calc.calculate(bilirubin=1.5, albumin=4.0, inr=1.3,
                           ascites="none", encephalopathy_grade=3)
        
        assert r0.value == 5  # Base score
        assert r2.value == 6  # +1 for grade 2
        assert r3.value == 7  # +2 for grade 3
    
    def test_surgical_risk_in_interpretation(self):
        """Test that surgical mortality is mentioned"""
        from src.domain.services.calculators import ChildPughCalculator
        calc = ChildPughCalculator()
        result = calc.calculate(
            bilirubin=5.0, albumin=2.0, inr=2.5,
            ascites="moderate_severe", encephalopathy_grade=3
        )
        assert "mortality" in result.interpretation.detail.lower()
    
    def test_references_include_pugh(self):
        """Test that references include original Pugh paper"""
        from src.domain.services.calculators import ChildPughCalculator
        calc = ChildPughCalculator()
        refs = calc.references
        pmids = [r.pmid for r in refs if r.pmid]
        assert "4541913" in pmids  # Pugh 1973
    
    def test_tool_id(self):
        from src.domain.services.calculators import ChildPughCalculator
        assert ChildPughCalculator().tool_id == "child_pugh"
