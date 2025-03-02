#!/usr/bin/env python3
import pytest
import json
import re
from unittest.mock import patch, MagicMock

from modal_infra import validate

class TestValidate:
    @pytest.fixture
    def mock_anthropic_response_valid(self):
        """Mock a valid response from Anthropic API"""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="""
        I've analyzed the changes in the diff against the provided instructions.
        
        The diff shows that the developer has implemented the requested feature correctly.
        The code changes align with the requirements specified in the instructions.
        
        <verdict>true</verdict>
        """)]
        return mock_response
    
    @pytest.fixture
    def mock_anthropic_response_invalid(self):
        """Mock an invalid response from Anthropic API"""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="""
        I've analyzed the changes in the diff against the provided instructions.
        
        The diff does not fully implement the requirements specified in the instructions.
        There are several missing components that were explicitly requested.
        
        <verdict>false</verdict>
        """)]
        return mock_response
    
    @pytest.fixture
    def mock_anthropic_response_no_verdict(self):
        """Mock a response from Anthropic API with no verdict"""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="""
        I've analyzed the changes in the diff against the provided instructions.
        
        The analysis is inconclusive as there are both matching and non-matching elements.
        """)]
        return mock_response
    
    @pytest.fixture
    def mock_anthropic_error(self):
        """Mock an error from Anthropic API"""
        return Exception("API Error")
    
    @patch('modal_infra.Anthropic')
    def test_validate_valid_changes(self, mock_anthropic_class, mock_anthropic_response_valid):
        """Test validation with valid changes"""
        # Setup
        mock_anthropic_instance = mock_anthropic_class.return_value
        mock_anthropic_instance.messages.create.return_value = mock_anthropic_response_valid
        
        # Test data
        diff = "Sample diff content"
        instructions = "Sample instructions"
        
        # Execute
        result = validate(diff, instructions)
        
        # Assert
        assert result["valid"] is True
        assert "APPROVED" in result["comment"]
        assert "✅" in result["comment"]
        
        # Verify API call
        mock_anthropic_instance.messages.create.assert_called_once()
        call_args = mock_anthropic_instance.messages.create.call_args[1]
        assert call_args["model"] == "claude-3-opus-20240229"
        assert call_args["temperature"] == 0
        assert diff in call_args["messages"][0]["content"]
        assert instructions in call_args["messages"][0]["content"]
    
    @patch('modal_infra.Anthropic')
    def test_validate_invalid_changes(self, mock_anthropic_class, mock_anthropic_response_invalid):
        """Test validation with invalid changes"""
        # Setup
        mock_anthropic_instance = mock_anthropic_class.return_value
        mock_anthropic_instance.messages.create.return_value = mock_anthropic_response_invalid
        
        # Test data
        diff = "Sample diff content"
        instructions = "Sample instructions"
        
        # Execute
        result = validate(diff, instructions)
        
        # Assert
        assert result["valid"] is False
        assert "CHANGES REQUESTED" in result["comment"]
        assert "❌" in result["comment"]
    
    @patch('modal_infra.Anthropic')
    def test_validate_no_verdict(self, mock_anthropic_class, mock_anthropic_response_no_verdict):
        """Test validation with no verdict in response"""
        # Setup
        mock_anthropic_instance = mock_anthropic_class.return_value
        mock_anthropic_instance.messages.create.return_value = mock_anthropic_response_no_verdict
        
        # Test data
        diff = "Sample diff content"
        instructions = "Sample instructions"
        
        # Execute
        result = validate(diff, instructions)
        
        # Assert
        assert result["valid"] is False
        assert "❌" in result["comment"]
    
    @patch('modal_infra.Anthropic')
    def test_validate_api_error(self, mock_anthropic_class, mock_anthropic_error):
        """Test validation with API error"""
        # Setup
        mock_anthropic_instance = mock_anthropic_class.return_value
        mock_anthropic_instance.messages.create.side_effect = mock_anthropic_error
        
        # Test data
        diff = "Sample diff content"
        instructions = "Sample instructions"
        
        # Execute
        result = validate(diff, instructions)
        
        # Assert
        assert result["valid"] is False
        assert "❌ Error during validation:" in result["comment"]
        assert "API Error" in result["comment"]

if __name__ == "__main__":
    pytest.main(["-v", "test_modal_infra.py"]) 