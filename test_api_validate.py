#!/usr/bin/env python3
import pytest
import json
from unittest.mock import patch, MagicMock

from modal_infra import api_validate, validate

class TestApiValidate:
    @pytest.fixture
    def mock_validate_result_valid(self):
        """Mock a valid result from validate function"""
        return {
            "valid": True,
            "comment": "## PR Validation Bot: ✅ APPROVED\n\nThe changes look good!"
        }
    
    @pytest.fixture
    def mock_validate_result_invalid(self):
        """Mock an invalid result from validate function"""
        return {
            "valid": False,
            "comment": "## PR Validation Bot: ❌ CHANGES REQUESTED\n\nThe changes don't match the requirements."
        }
    
    @patch('modal_infra.validate')
    def test_api_validate_valid(self, mock_validate, mock_validate_result_valid):
        """Test API endpoint with valid validation result"""
        # Setup
        mock_validate.return_value = mock_validate_result_valid
        
        # Test data
        diff = "Sample diff content"
        instructions = "Sample instructions"
        
        # Execute
        result = api_validate(diff, instructions)
        
        # Assert
        assert result["valid"] is True
        assert "APPROVED" in result["comment"]
        
        # Verify validate function was called with correct parameters
        mock_validate.assert_called_once_with(diff, instructions)
    
    @patch('modal_infra.validate')
    def test_api_validate_invalid(self, mock_validate, mock_validate_result_invalid):
        """Test API endpoint with invalid validation result"""
        # Setup
        mock_validate.return_value = mock_validate_result_invalid
        
        # Test data
        diff = "Sample diff content"
        instructions = "Sample instructions"
        
        # Execute
        result = api_validate(diff, instructions)
        
        # Assert
        assert result["valid"] is False
        assert "CHANGES REQUESTED" in result["comment"]
        
        # Verify validate function was called with correct parameters
        mock_validate.assert_called_once_with(diff, instructions)

if __name__ == "__main__":
    pytest.main(["-v", "test_api_validate.py"]) 