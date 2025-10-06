"""
Test suite for math_helper module
Following TDD principles - tests written before implementation
"""
import pytest
from src.utils.math_helper import calculate_profit, calculate_roi, format_currency


class TestCalculateProfit:
    """Tests for calculate_profit function"""
    
    def test_calculate_profit_basic(self):
        """Test basic profit calculation with default fee"""
        assert calculate_profit(100.0, 75.0, 10.0) == 15.0  # $100 - $75 - $10 fee
    
    def test_calculate_profit_no_profit(self):
        """Test loss scenario"""
        assert calculate_profit(50.0, 60.0, 10.0) == -15.0  # Loss scenario
    
    def test_calculate_profit_zero_fee(self):
        """Test with no fees"""
        assert calculate_profit(100.0, 75.0, 0.0) == 25.0
    
    def test_calculate_profit_high_fee(self):
        """Test with fees exceeding 100%"""
        assert calculate_profit(100.0, 50.0, 150.0) == -100.0  # Fee > 100%
    
    def test_calculate_profit_negative_prices(self):
        """Test edge case with negative prices"""
        with pytest.raises(ValueError, match="Prices cannot be negative"):
            calculate_profit(-100.0, 50.0, 10.0)


class TestCalculateROI:
    """Tests for calculate_roi function"""
    
    def test_calculate_roi_positive(self):
        """Test positive ROI calculation"""
        assert calculate_roi(25.0, 100.0) == 0.25  # 25% ROI
    
    def test_calculate_roi_negative(self):
        """Test negative ROI (loss)"""
        assert calculate_roi(-25.0, 100.0) == -0.25  # -25% ROI
    
    def test_calculate_roi_zero_profit(self):
        """Test break-even scenario"""
        assert calculate_roi(0.0, 100.0) == 0.0
    
    def test_calculate_roi_zero_cost(self):
        """Test edge case with zero cost price"""
        with pytest.raises(ValueError, match="Cost price cannot be zero"):
            calculate_roi(25.0, 0.0)
    
    def test_calculate_roi_large_numbers(self):
        """Test with large numbers"""
        assert calculate_roi(1000000.0, 100000.0) == 10.0  # 1000% ROI


class TestFormatCurrency:
    """Tests for format_currency function"""
    
    def test_format_currency_positive(self):
        """Test positive amount formatting"""
        assert format_currency(123.45) == "$123.45"
    
    def test_format_currency_negative(self):
        """Test negative amount with parentheses"""
        assert format_currency(-50.0) == "($50.00)"
    
    def test_format_currency_zero(self):
        """Test zero amount"""
        assert format_currency(0.0) == "$0.00"
    
    def test_format_currency_rounding(self):
        """Test proper rounding to 2 decimal places"""
        assert format_currency(123.456) == "$123.46"
        assert format_currency(123.454) == "$123.45"
    
    def test_format_currency_large_numbers(self):
        """Test formatting with thousands"""
        assert format_currency(1234567.89) == "$1,234,567.89"
    
    def test_format_currency_small_negative(self):
        """Test small negative amounts"""
        assert format_currency(-0.01) == "($0.01)"


class TestIntegration:
    """Integration tests for combined functionality"""
    
    def test_profit_to_roi_pipeline(self):
        """Test calculating profit then ROI"""
        profit = calculate_profit(150.0, 100.0, 10.0)
        roi = calculate_roi(profit, 100.0)
        assert roi == 0.40  # 40% ROI
    
    def test_format_profit_output(self):
        """Test formatting calculated profit"""
        profit = calculate_profit(150.0, 100.0, 10.0)
        formatted = format_currency(profit)
        assert formatted == "$40.00"
    
    def test_negative_profit_formatting(self):
        """Test formatting loss scenarios"""
        profit = calculate_profit(80.0, 100.0, 10.0)
        formatted = format_currency(profit)
        assert formatted == "($30.00)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])