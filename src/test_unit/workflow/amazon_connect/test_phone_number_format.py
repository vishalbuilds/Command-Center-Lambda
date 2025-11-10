"""
Unit tests for phone_number_format module.
"""
import pytest
from unittest.mock import patch, MagicMock
from workflow.amazon_connect.phone_number_format import PhoneNumberFormat


class TestPhoneNumberFormat:
    
    def test_init(self):
        """Test PhoneNumberFormat initialization."""
        event = {"phone_number": "+14155552671"}
        
        instance = PhoneNumberFormat(event)
        
        assert instance.event == event
        assert instance.phone_number == "+14155552671"
    
    def test_init_without_phone_number(self):
        """Test initialization without phone_number."""
        event = {"other_data": "value"}
        
        instance = PhoneNumberFormat(event)
        
        assert instance.phone_number is None
    
    def test_do_validate_success(self):
        """Test successful validation."""
        event = {"phone_number": "+14155552671"}
        
        instance = PhoneNumberFormat(event)
        result, error = instance.do_validate()
        
        assert result is True
        assert error is None
    
    def test_do_validate_missing_phone_number(self):
        """Test validation with missing phone_number."""
        event = {}
        
        instance = PhoneNumberFormat(event)
        result, error = instance.do_validate()
        
        assert result is False
        assert error == "Phone number is required in event"
    
    def test_do_operation_valid_us_number_with_plus(self):
        """Test do_operation with valid US number with plus sign."""
        event = {"phone_number": "+14155552671"}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        assert result["validationResult"] == "Valid"
        assert result["countryCode"] == 1
        assert result["regionCode"] == "US"
        assert result["phoneNumber"] == 4155552671
    
    def test_do_operation_valid_us_number_without_plus(self):
        """Test do_operation with valid US number without plus sign."""
        event = {"phone_number": "14155552671"}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        assert result["validationResult"] == "Valid"
        assert result["countryCode"] == 1
        assert result["regionCode"] == "US"
    
    def test_do_operation_valid_uk_number(self):
        """Test do_operation with valid UK number."""
        event = {"phone_number": "+442071838750"}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        assert result["validationResult"] == "Valid"
        assert result["countryCode"] == 44
        assert result["regionCode"] == "GB"
    
    def test_do_operation_valid_india_number(self):
        """Test do_operation with valid India number."""
        event = {"phone_number": "+919876543210"}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        assert result["validationResult"] == "Valid"
        assert result["countryCode"] == 91
        assert result["regionCode"] == "IN"
    
    def test_do_operation_invalid_number(self):
        """Test do_operation with invalid number."""
        event = {"phone_number": "+1234"}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        assert result["validationResult"] == "Invalid"
        assert "failedReason" in result
    
    def test_do_operation_invalid_format(self):
        """Test do_operation with invalid format."""
        event = {"phone_number": "abc123"}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        assert result["validationResult"] == "Error"
        assert "failedReason" in result
    
    def test_do_operation_empty_string(self):
        """Test do_operation with empty string."""
        event = {"phone_number": ""}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        assert result["validationResult"] == "Error"
        assert "failedReason" in result
    
    def test_do_operation_numeric_phone_number(self):
        """Test do_operation with numeric phone number."""
        event = {"phone_number": 14155552671}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        assert result["validationResult"] == "Valid"
        assert result["countryCode"] == 1
    
    def test_do_operation_too_short_number(self):
        """Test do_operation with too short number."""
        event = {"phone_number": "+1415"}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        assert result["validationResult"] == "Invalid"
    
    def test_do_operation_too_long_number(self):
        """Test do_operation with too long number."""
        event = {"phone_number": "+141555526711234567890"}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        # Too long numbers cause parse exception, returning "Error"
        assert result["validationResult"] == "Error"
        assert "failedReason" in result
    
    def test_do_operation_special_characters(self):
        """Test do_operation with special characters."""
        event = {"phone_number": "+1-415-555-2671"}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        # phonenumbers library should handle dashes
        assert result["validationResult"] in ["Valid", "Invalid"]
    
    def test_do_operation_with_spaces(self):
        """Test do_operation with spaces in number."""
        event = {"phone_number": "+1 415 555 2671"}
        
        instance = PhoneNumberFormat(event)
        result = instance.do_operation()
        
        # phonenumbers library should handle spaces
        assert result["validationResult"] in ["Valid", "Invalid"]
