"""
Base Calculator Class

Abstract base class for all medical calculators.
Defines the interface that all calculators must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..entities.score_result import ScoreResult
from ..entities.tool_metadata import ToolMetadata


class BaseCalculator(ABC):
    """
    Abstract base class for all medical calculators.
    
    Every calculator must:
    1. Provide metadata (tool_id, name, keys, references)
    2. Implement the calculate() method
    3. Return a ScoreResult with full clinical context
    
    Example:
        class CkdEpi2021Calculator(BaseCalculator):
            
            @property
            def metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    low_level=LowLevelKey(...),
                    high_level=HighLevelKey(...),
                    references=[Reference(...)]
                )
            
            def calculate(self, age: int, sex: str, serum_creatinine: float) -> ScoreResult:
                # Implementation
                pass
    """
    
    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """
        Return the tool metadata.
        
        Must include:
        - LowLevelKey for precise identification
        - HighLevelKey for discovery
        - References to original papers
        """
        pass
    
    @abstractmethod
    def calculate(self, *args: Any, **kwargs: Any) -> ScoreResult:
        """
        Execute the calculation.
        
        Args:
            *args: Calculator-specific positional parameters
            **kwargs: Calculator-specific keyword parameters
            
        Returns:
            ScoreResult with value, interpretation, and references
        """
        pass
    
    # Convenience properties
    
    @property
    def tool_id(self) -> str:
        """Get the unique tool identifier"""
        return self.metadata.tool_id
    
    @property
    def name(self) -> str:
        """Get the human-readable name"""
        return self.metadata.name
    
    @property
    def low_level_key(self):
        """Get the low level key for precise identification"""
        return self.metadata.low_level
    
    @property
    def high_level_key(self):
        """Get the high level key for discovery"""
        return self.metadata.high_level
    
    @property
    def references(self):
        """Get the original paper references"""
        return self.metadata.references
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Get the input parameter schema.
        Override in subclass for detailed schema.
        """
        return {
            "params": self.metadata.low_level.input_params,
            "output": self.metadata.low_level.output_type
        }
    
    def validate_inputs(self, **params) -> None:
        """
        Validate input parameters.
        Override in subclass for specific validation.
        Raises ValueError if validation fails.
        """
        required = self.metadata.low_level.input_params
        for param in required:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(tool_id='{self.tool_id}')"
