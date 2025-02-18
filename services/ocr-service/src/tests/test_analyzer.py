import pytest
from datetime import datetime

from ..core.analyzer import TextAnalyzer, Company, Booth, AnalysisResult
from ..core.preprocessor import Region
from ..core.errors import ValidationError

@pytest.fixture
def sample_text():
    """Sample OCR text for testing"""
    return """
    Floor Plan - Hall A
    
    Company: Test Corporation
    Booth: A123
    20x30 sq ft
    
    ACME Industries (Booth B456)
    Space: 400 sq ft
    
    Global Systems Inc
    #C789
    15x20
    
    Invalid Company
    No booth info
    """

@pytest.fixture
def analyzer():
    """Create TextAnalyzer instance"""
    return TextAnalyzer()

@pytest.mark.asyncio
async def test_analyze_valid_text(analyzer, sample_text):
    """Test complete text analysis with valid input"""
    result = await analyzer.analyze(sample_text)
    
    # Verify result structure
    assert isinstance(result, AnalysisResult)
    assert isinstance(result.companies, list)
    assert isinstance(result.booths, list)
    assert isinstance(result.confidence, float)
    assert isinstance(result.processing_time, float)
    assert result.raw_text == sample_text
    
    # Verify companies were extracted
    assert len(result.companies) >= 3
    assert any(c.name == "Test Corporation" for c in result.companies)
    assert any(c.name == "ACME Industries" for c in result.companies)
    assert any(c.name == "Global Systems Inc" for c in result.companies)
    
    # Verify booths were extracted
    assert len(result.booths) >= 3
    assert any(b.id == "A123" for b in result.booths)
    assert any(b.id == "B456" for b in result.booths)
    assert any(b.id == "C789" for b in result.booths)
    
    # Verify confidence score
    assert 0 <= result.confidence <= 1

@pytest.mark.asyncio
async def test_extract_companies(analyzer, sample_text):
    """Test company name extraction"""
    companies = await analyzer._extract_companies(sample_text)
    
    # Verify extracted companies
    assert len(companies) >= 3
    
    # Check specific company details
    test_corp = next(c for c in companies if c.name == "Test Corporation")
    assert test_corp.booth_id == "A123"
    assert 0 <= test_corp.confidence <= 1
    
    acme = next(c for c in companies if c.name == "ACME Industries")
    assert acme.booth_id == "B456"
    assert 0 <= acme.confidence <= 1

@pytest.mark.asyncio
async def test_extract_booth_info(analyzer, sample_text):
    """Test booth information extraction"""
    booths = await analyzer._extract_booth_info(sample_text)
    
    # Verify extracted booths
    assert len(booths) >= 3
    
    # Check specific booth details
    booth_a = next(b for b in booths if b.id == "A123")
    assert booth_a.size == 600  # 20x30
    assert 0 <= booth_a.confidence <= 1
    
    booth_b = next(b for b in booths if b.id == "B456")
    assert booth_b.size == 400  # 400 sq ft
    assert 0 <= booth_b.confidence <= 1

@pytest.mark.asyncio
async def test_match_companies_to_booths(analyzer):
    """Test matching companies with booths"""
    companies = [
        Company("Test Corp", "A123", 0.8, None),
        Company("ACME Inc", "B456", 0.9, None),
        Company("No Booth Corp", "", 0.7, None)
    ]
    
    booths = [
        Booth("A123", 600, "Hall A", 0.85),
        Booth("B456", 400, "Hall A", 0.95),
        Booth("C789", 300, "Hall A", 0.80)
    ]
    
    await analyzer._match_companies_to_booths(companies, booths)
    
    # Verify matches
    test_corp = next(c for c in companies if c.name == "Test Corp")
    assert test_corp.confidence == (0.8 + 0.85) / 2
    
    acme = next(c for c in companies if c.name == "ACME Inc")
    assert acme.confidence == (0.9 + 0.95) / 2

@pytest.mark.asyncio
async def test_confidence_calculation(analyzer):
    """Test confidence score calculations"""
    # Test company name confidence
    high_conf = analyzer._calculate_name_confidence(
        "ACME Corporation Inc",
        "Company: ACME Corporation Inc (Booth A123)"
    )
    assert high_conf > 0.8  # Should be high confidence
    
    low_conf = analyzer._calculate_name_confidence(
        "x123",
        "Some random text x123"
    )
    assert low_conf < 0.5  # Should be low confidence
    
    # Test booth confidence
    booth_high = analyzer._calculate_booth_confidence(
        "A123",
        "Booth A123 (400 sq ft)"
    )
    assert booth_high > 0.8  # Should be high confidence
    
    booth_low = analyzer._calculate_booth_confidence(
        "XYZ",
        "Random text XYZ"
    )
    assert booth_low < 0.5  # Should be low confidence

@pytest.mark.asyncio
async def test_validation(analyzer):
    """Test result validation"""
    # Test with no companies
    with pytest.raises(ValidationError) as exc_info:
        result = AnalysisResult(
            companies=[],
            booths=[Booth("A123", 400, "Hall A", 0.9)],
            confidence=0.9,
            processing_time=1.0,
            raw_text="Sample text"
        )
        analyzer._validate_result(result)
    assert "No companies extracted" in str(exc_info.value)
    
    # Test with no booths
    with pytest.raises(ValidationError) as exc_info:
        result = AnalysisResult(
            companies=[Company("Test Corp", "A123", 0.9, None)],
            booths=[],
            confidence=0.9,
            processing_time=1.0,
            raw_text="Sample text"
        )
        analyzer._validate_result(result)
    assert "No booths extracted" in str(exc_info.value)
    
    # Test with low confidence
    with pytest.raises(ValidationError) as exc_info:
        result = AnalysisResult(
            companies=[Company("Test Corp", "A123", 0.4, None)],
            booths=[Booth("A123", 400, "Hall A", 0.4)],
            confidence=0.4,
            processing_time=1.0,
            raw_text="Sample text"
        )
        analyzer._validate_result(result)
    assert "Low confidence score" in str(exc_info.value)

@pytest.mark.asyncio
async def test_error_handling(analyzer):
    """Test error handling in text analysis"""
    # Test with empty text
    with pytest.raises(ValidationError) as exc_info:
        await analyzer.analyze("")
    assert "Text analysis failed" in str(exc_info.value)
    
    # Test with invalid text format
    with pytest.raises(ValidationError) as exc_info:
        await analyzer.analyze("123\n456\n789")
    assert "validation failed" in str(exc_info.value)