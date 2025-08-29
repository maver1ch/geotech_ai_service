#!/usr/bin/env python3
"""
Test script for Geotech Calculators
Verify both settlement and bearing capacity calculations
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.agentic_workflow.tools.geotech_calculators import (
    settlement_calculator,
    bearing_capacity_calculator,
    get_available_tools,
    call_tool
)

def test_settlement_calculator():
    """Test settlement calculator with various inputs"""
    print("=" * 50)
    print("TESTING SETTLEMENT CALCULATOR")
    print("=" * 50)
    
    # Test case 1: Normal calculation
    print("Test 1: Normal calculation (load=100, E=5000)")
    result = settlement_calculator(load=100, young_modulus=5000)
    print(f"Result: {result}")
    
    # Test case 2: Different values
    print("\nTest 2: Different values (load=250, E=12000)")
    result = settlement_calculator(load=250, young_modulus=12000)
    print(f"Result: {result}")
    
    # Test case 3: Error case - negative load
    print("\nTest 3: Error case (negative load)")
    result = settlement_calculator(load=-50, young_modulus=5000)
    print(f"Result: {result}")
    
    # Test case 4: Error case - zero modulus
    print("\nTest 4: Error case (zero modulus)")
    result = settlement_calculator(load=100, young_modulus=0)
    print(f"Result: {result}")

def test_bearing_capacity_calculator():
    """Test bearing capacity calculator with various inputs"""
    print("\n" + "=" * 50)
    print("TESTING BEARING CAPACITY CALCULATOR")
    print("=" * 50)
    
    # Test case 1: Normal calculation (φ=30°)
    print("Test 1: Normal calculation (B=2, γ=18, Df=1.5, φ=30)")
    result = bearing_capacity_calculator(B=2.0, gamma=18.0, Df=1.5, phi=30)
    print(f"Result: {result}")
    
    # Test case 2: Different angle (φ=25°)
    print("\nTest 2: Different angle (B=1.5, γ=19, Df=2.0, φ=25)")
    result = bearing_capacity_calculator(B=1.5, gamma=19.0, Df=2.0, phi=25)
    print(f"Result: {result}")
    
    # Test case 3: Edge case (φ=0°, cohesionless)
    print("\nTest 3: Edge case φ=0° (B=2, γ=16, Df=1, φ=0)")
    result = bearing_capacity_calculator(B=2.0, gamma=16.0, Df=1.0, phi=0)
    print(f"Result: {result}")
    
    # Test case 4: Interpolation test (φ=17°, between 15° and 20°)
    print("\nTest 4: Interpolation test φ=17° (B=2, γ=18, Df=1, φ=17)")
    result = bearing_capacity_calculator(B=2.0, gamma=18.0, Df=1.0, phi=17)
    print(f"Result: {result}")
    
    # Test case 5: Error case - invalid phi
    print("\nTest 5: Error case (φ=50° > 40°)")
    result = bearing_capacity_calculator(B=2.0, gamma=18.0, Df=1.0, phi=50)
    print(f"Result: {result}")
    
    # Test case 6: Error case - negative width
    print("\nTest 6: Error case (negative width)")
    result = bearing_capacity_calculator(B=-1.0, gamma=18.0, Df=1.0, phi=30)
    print(f"Result: {result}")

def test_tool_integration():
    """Test generic tool calling interface"""
    print("\n" + "=" * 50)
    print("TESTING TOOL INTEGRATION")
    print("=" * 50)
    
    print("Available tools:", get_available_tools())
    
    # Test via generic interface
    print("\nTest settlement via call_tool:")
    result = call_tool("settlement_calculator", load=150, young_modulus=8000)
    print(f"Result: {result}")
    
    print("\nTest bearing capacity via call_tool:")
    result = call_tool("bearing_capacity_calculator", B=2.5, gamma=17.0, Df=1.2, phi=28)
    print(f"Result: {result}")
    
    print("\nTest unknown tool:")
    result = call_tool("unknown_tool", param=123)
    print(f"Result: {result}")

if __name__ == "__main__":
    print("🧪 GEOTECH TOOLS TEST SUITE")
    print("Testing geotechnical calculation tools...")
    
    test_settlement_calculator()
    test_bearing_capacity_calculator() 
    test_tool_integration()
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 50)
    print("Check results above for any errors or unexpected behavior")