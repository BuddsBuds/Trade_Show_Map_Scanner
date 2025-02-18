import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .errors import ValidationError
from .preprocessor import Region

@dataclass
class Company:
    """Extracted company information"""
    name: str
    booth_id: str
    confidence: float
    region: Optional[Region] = None

@dataclass
class Booth:
    """Extracted booth information"""
    id: str
    size: Optional[float]
    location: Optional[str]
    confidence: float

@dataclass
class AnalysisResult:
    """Result of text analysis"""
    companies: List[Company]
    booths: List[Booth]
    confidence: float
    processing_time: float
    raw_text: str

class TextAnalyzer:
    """Analyze extracted text for company info"""
    
    def __init__(self):
        # Common company name patterns
        self.company_patterns = [
            r'Company:\s*([A-Za-z0-9\s&]+)',
            r'Booth:\s*([A-Za-z0-9\s&]+)',
            r'^([A-Z][A-Za-z0-9\s&]+)$',
            r'([A-Z][A-Za-z0-9\s&]+)\s+\(Booth\s+[A-Z0-9]+\)'
        ]
        
        # Booth information patterns
        self.booth_patterns = [
            r'Booth\s+([A-Z0-9]+)',
            r'#([A-Z0-9]+)',
            r'Space\s+([A-Z0-9]+)'
        ]
        
        # Size patterns (in square feet/meters)
        self.size_patterns = [
            r'(\d+)\s*(?:sq\.?\s*(?:ft|feet|m))',
            r'(\d+)\s*(?:square\s*(?:ft|feet|m))',
            r'(\d+)\s*[xX]\s*(\d+)'  # Dimensions like 10x20
        ]
    
    async def analyze(self, text: str) -> AnalysisResult:
        """
        Extract company names and booth info
        
        Args:
            text: OCR extracted text
            
        Returns:
            AnalysisResult: Analysis result containing extracted information
            
        Raises:
            ValidationError: If analysis fails validation
        """
        start_time = datetime.utcnow()
        
        try:
            # Extract companies and booths
            companies = await self._extract_companies(text)
            booths = await self._extract_booth_info(text)
            
            # Match companies with booths
            await self._match_companies_to_booths(companies, booths)
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(companies, booths)
            
            result = AnalysisResult(
                companies=companies,
                booths=booths,
                confidence=confidence,
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                raw_text=text
            )
            
            # Validate result
            self._validate_result(result)
            
            return result
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(
                message=f"Text analysis failed: {str(e)}",
                validation_errors={"error": str(e)}
            )
    
    async def _extract_companies(self, text: str) -> List[Company]:
        """Extract company names using pattern matching"""
        companies = []
        lines = text.split('\n')
        
        for line in lines:
            for pattern in self.company_patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    company_name = match.group(1).strip()
                    # Skip if too short or looks like noise
                    if len(company_name) < 3 or not re.search(r'[A-Za-z]', company_name):
                        continue
                        
                    # Look for booth ID in the same line
                    booth_id = None
                    for booth_pattern in self.booth_patterns:
                        booth_match = re.search(booth_pattern, line)
                        if booth_match:
                            booth_id = booth_match.group(1)
                            break
                    
                    # Calculate confidence based on pattern match and context
                    confidence = self._calculate_name_confidence(company_name, line)
                    
                    companies.append(Company(
                        name=company_name,
                        booth_id=booth_id or "",
                        confidence=confidence,
                        region=None  # Will be set when matching with regions
                    ))
        
        return companies
    
    async def _extract_booth_info(self, text: str) -> List[Booth]:
        """Extract booth information"""
        booths = []
        lines = text.split('\n')
        
        for line in lines:
            # Extract booth ID
            for pattern in self.booth_patterns:
                match = re.search(pattern, line)
                if match:
                    booth_id = match.group(1)
                    
                    # Extract size if available
                    size = None
                    for size_pattern in self.size_patterns:
                        size_match = re.search(size_pattern, line)
                        if size_match:
                            if len(size_match.groups()) == 2:  # Dimensions pattern
                                length, width = map(int, size_match.groups())
                                size = length * width
                            else:
                                size = int(size_match.group(1))
                            break
                    
                    # Calculate confidence based on pattern match and context
                    confidence = self._calculate_booth_confidence(booth_id, line)
                    
                    booths.append(Booth(
                        id=booth_id,
                        size=size,
                        location=None,  # Will be set when processing floor plan
                        confidence=confidence
                    ))
        
        return booths
    
    async def _match_companies_to_booths(
        self,
        companies: List[Company],
        booths: List[Booth]
    ) -> None:
        """Match companies with their corresponding booths"""
        booth_map = {booth.id: booth for booth in booths}
        
        for company in companies:
            if company.booth_id and company.booth_id in booth_map:
                # Update company confidence based on booth match
                booth = booth_map[company.booth_id]
                company.confidence = (company.confidence + booth.confidence) / 2
    
    def _calculate_name_confidence(self, name: str, context: str) -> float:
        """Calculate confidence score for extracted company name"""
        confidence = 0.0
        
        # Check for common company indicators
        if re.search(r'Company|Corp|Inc|LLC|Ltd', name):
            confidence += 0.2
        
        # Check for proper capitalization
        if re.match(r'^[A-Z][a-z]', name):
            confidence += 0.2
        
        # Check for reasonable length
        if 3 <= len(name.split()) <= 5:
            confidence += 0.2
        
        # Check for context
        if 'Booth' in context or 'Space' in context:
            confidence += 0.2
        
        # Check for noise
        if re.search(r'[^A-Za-z0-9\s&\']', name):
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence + 0.2))  # Base confidence of 0.2
    
    def _calculate_booth_confidence(self, booth_id: str, context: str) -> float:
        """Calculate confidence score for extracted booth information"""
        confidence = 0.0
        
        # Check for common booth number patterns
        if re.match(r'^[A-Z]\d+$|^\d+$', booth_id):
            confidence += 0.3
        
        # Check for reasonable length
        if 2 <= len(booth_id) <= 5:
            confidence += 0.2
        
        # Check for context
        if 'Booth' in context or 'Space' in context:
            confidence += 0.3
        
        # Check for size information
        if any(re.search(pattern, context) for pattern in self.size_patterns):
            confidence += 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_confidence(
        self,
        companies: List[Company],
        booths: List[Booth]
    ) -> float:
        """Calculate overall confidence score"""
        if not companies and not booths:
            return 0.0
            
        total_confidence = 0.0
        total_items = 0
        
        # Sum company confidences
        if companies:
            total_confidence += sum(c.confidence for c in companies)
            total_items += len(companies)
        
        # Sum booth confidences
        if booths:
            total_confidence += sum(b.confidence for b in booths)
            total_items += len(booths)
        
        return total_confidence / total_items
    
    def _validate_result(self, result: AnalysisResult) -> None:
        """Validate analysis result"""
        validation_errors = {}
        
        # Check if any companies were found
        if not result.companies:
            validation_errors["companies"] = "No companies extracted"
        
        # Check if any booths were found
        if not result.booths:
            validation_errors["booths"] = "No booths extracted"
        
        # Check overall confidence
        if result.confidence < 0.5:
            validation_errors["confidence"] = f"Low confidence score: {result.confidence}"
        
        # Check for unmatched companies
        unmatched = [c for c in result.companies if not c.booth_id]
        if unmatched:
            validation_errors["unmatched"] = f"{len(unmatched)} companies without booth IDs"
        
        if validation_errors:
            raise ValidationError(
                message="Analysis validation failed",
                validation_errors=validation_errors
            )