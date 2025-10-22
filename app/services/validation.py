from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    """Data validation result"""
    is_valid: bool = Field(
        ...,
        description="Whether validation passed"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="List of validation errors"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of validation warnings"
    )

class DataValidator:
    """Validates input data quality and completeness"""
    def __init__(self):
        self.required_fields = {
            'treatment_schedule': [
                'treatments',
                'datetime',
                'type'
            ],
            'sleep_data': [
                'sleep_time',
                'wake_time',
                'quality'
            ],
            'energy_reports': [
                'timestamp',
                'level',
                'notes'
            ]
        }
        
        self.data_types = {
            'treatment_schedule.treatments': list,
            'treatment_schedule.datetime': str,
            'treatment_schedule.type': str,
            'sleep_data.sleep_time': str,
            'sleep_data.wake_time': str,
            'sleep_data.quality': float,
            'energy_reports.timestamp': str,
            'energy_reports.level': float,
            'energy_reports.notes': str
        }
        
        self.value_ranges = {
            'sleep_data.quality': (0, 10),
            'energy_reports.level': (0, 10)
        }
        
    async def validate_data(
        self,
        data: Dict[str, Any],
        schema_name: str
    ) -> ValidationResult:
        """Validate data against schema"""
        try:
            errors = []
            warnings = []
            
            # Check required fields
            missing = self._check_required_fields(
                data,
                schema_name
            )
            if missing:
                errors.extend([
                    f"Missing required field: {field}"
                    for field in missing
                ])
                
            # Validate data types
            type_errors = self._validate_data_types(
                data,
                schema_name
            )
            errors.extend(type_errors)
            
            # Validate value ranges
            range_errors = self._validate_value_ranges(
                data,
                schema_name
            )
            errors.extend(range_errors)
            
            # Additional schema-specific validation
            specific_errors = await self._validate_schema_specific(
                data,
                schema_name
            )
            errors.extend(specific_errors)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Data validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[str(e)]
            )
            
    def _check_required_fields(
        self,
        data: Dict[str, Any],
        schema_name: str
    ) -> List[str]:
        """Check for missing required fields"""
        missing = []
        
        if schema_name not in self.required_fields:
            return missing
            
        for field in self.required_fields[schema_name]:
            if field not in data:
                missing.append(field)
                
        return missing
        
    def _validate_data_types(
        self,
        data: Dict[str, Any],
        schema_name: str
    ) -> List[str]:
        """Validate data types of fields"""
        errors = []
        
        for field_key, expected_type in self.data_types.items():
            schema, field = field_key.split('.')
            
            if schema == schema_name and field in data:
                value = data[field]
                if not isinstance(value, expected_type):
                    errors.append(
                        f"Invalid type for {field}: expected "
                        f"{expected_type.__name__}, got "
                        f"{type(value).__name__}"
                    )
                    
        return errors
        
    def _validate_value_ranges(
        self,
        data: Dict[str, Any],
        schema_name: str
    ) -> List[str]:
        """Validate numeric value ranges"""
        errors = []
        
        for field_key, (min_val, max_val) in self.value_ranges.items():
            schema, field = field_key.split('.')
            
            if schema == schema_name and field in data:
                value = data[field]
                if not min_val <= value <= max_val:
                    errors.append(
                        f"Value for {field} must be between "
                        f"{min_val} and {max_val}"
                    )
                    
        return errors
        
    async def _validate_schema_specific(
        self,
        data: Dict[str, Any],
        schema_name: str
    ) -> List[str]:
        """Schema-specific validation rules"""
        errors = []
        
        if schema_name == 'treatment_schedule':
            errors.extend(
                self._validate_treatment_schedule(data)
            )
        elif schema_name == 'sleep_data':
            errors.extend(
                self._validate_sleep_data(data)
            )
        elif schema_name == 'energy_reports':
            errors.extend(
                self._validate_energy_reports(data)
            )
            
        return errors
        
    def _validate_treatment_schedule(
        self,
        data: Dict[str, Any]
    ) -> List[str]:
        """Validate treatment schedule data"""
        errors = []
        
        if 'treatments' in data:
            treatments = data['treatments']
            
            if not isinstance(treatments, list):
                errors.append(
                    "Treatments must be a list"
                )
                return errors
                
            for treatment in treatments:
                if not isinstance(treatment, dict):
                    errors.append(
                        "Each treatment must be a dictionary"
                    )
                    continue
                    
                if 'datetime' not in treatment:
                    errors.append(
                        "Treatment missing datetime"
                    )
                    
                if 'type' not in treatment:
                    errors.append(
                        "Treatment missing type"
                    )
                    
        return errors
        
    def _validate_sleep_data(
        self,
        data: Dict[str, Any]
    ) -> List[str]:
        """Validate sleep data"""
        errors = []
        
        if 'sleep_time' in data and 'wake_time' in data:
            sleep = data['sleep_time']
            wake = data['wake_time']
            
            if wake < sleep:
                errors.append(
                    "Wake time cannot be before sleep time"
                )
                
        if 'quality' in data:
            quality = data['quality']
            
            if not isinstance(quality, (int, float)):
                errors.append(
                    "Sleep quality must be a number"
                )
                
        return errors
        
    def _validate_energy_reports(
        self,
        data: Dict[str, Any]
    ) -> List[str]:
        """Validate energy report data"""
        errors = []
        
        if 'timestamp' not in data:
            errors.append("Missing timestamp")
            
        if 'level' in data:
            level = data['level']
            
            if not isinstance(level, (int, float)):
                errors.append(
                    "Energy level must be a number"
                )
                
        return errors