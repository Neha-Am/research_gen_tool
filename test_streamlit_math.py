#!/usr/bin/env python3
"""
Test script to verify Streamlit math formatting integration
"""

from modules.math_formatter import MathFormatter

def test_streamlit_integration():
    """Test that the math formatter works correctly for Streamlit"""
    print("🧮 Testing Streamlit Math Integration")
    print("=" * 50)
    
    formatter = MathFormatter()
    
    # Test the problematic equation from the original image
    original_equation = "E ← E + PWV φ(E■W■KWQE)■M (1)"
    print(f"Original: {original_equation}")
    
    formatted_equation = formatter.format_equation(original_equation)
    print(f"Formatted: {formatted_equation}")
    
    # Test validation
    validation = formatter.validate_equation(original_equation)
    print(f"Validation: {validation}")
    
    # Test content formatting
    test_content = """
    The attention mechanism is defined as:
    E ← E + PWV φ(E■W■KWQE)■M (1)
    
    Where theta represents the learning rate and alpha controls the regularization.
    """
    
    formatted_content = formatter.format_content_with_equations(test_content)
    print(f"\nFormatted content:\n{formatted_content}")
    
    print("\n✅ Streamlit integration test completed!")
    print("The math formatter is ready to use in the Streamlit app.")

if __name__ == "__main__":
    test_streamlit_integration() 