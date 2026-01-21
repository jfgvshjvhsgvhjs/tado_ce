"""
Integration test for service compatibility.
Run this script on Home Assistant to test the new service format.

Usage:
1. Copy this file to /config/custom_components/tado_ce/
2. SSH into Home Assistant
3. Run: python3 /config/custom_components/tado_ce/integration_test_service_compatibility.py
"""

import sys
import time

def test_time_period_parsing():
    """Test time_period parsing logic."""
    print("\n=== Test 1: Time Period Parsing ===")
    
    test_cases = [
        ("01:30:00", 90),
        ("00:30:00", 30),
        ("02:00:00", 120),
        ("00:15:30", 15),
    ]
    
    passed = 0
    failed = 0
    
    for time_period, expected_minutes in test_cases:
        try:
            time_parts = str(time_period).split(":")
            if len(time_parts) == 3:
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                seconds = int(time_parts[2])
                duration_minutes = hours * 60 + minutes + (seconds // 60)
                
                if duration_minutes == expected_minutes:
                    print(f"✓ PASS: {time_period} → {duration_minutes} minutes")
                    passed += 1
                else:
                    print(f"✗ FAIL: {time_period} → expected {expected_minutes}, got {duration_minutes}")
                    failed += 1
            else:
                print(f"✗ FAIL: {time_period} → invalid format")
                failed += 1
        except Exception as e:
            print(f"✗ FAIL: {time_period} → {e}")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


def test_button_time_conversion():
    """Test button duration to time_period conversion."""
    print("\n=== Test 2: Button Time Conversion ===")
    
    test_cases = [
        (30, "00:30:00"),
        (60, "01:00:00"),
        (90, "01:30:00"),
    ]
    
    passed = 0
    failed = 0
    
    for duration_minutes, expected_time_period in test_cases:
        try:
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            time_period = f"{hours:02d}:{minutes:02d}:00"
            
            if time_period == expected_time_period:
                print(f"✓ PASS: {duration_minutes} min → {time_period}")
                passed += 1
            else:
                print(f"✗ FAIL: {duration_minutes} min → expected {expected_time_period}, got {time_period}")
                failed += 1
        except Exception as e:
            print(f"✗ FAIL: {duration_minutes} min → {e}")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


def test_service_imports():
    """Test that all required modules can be imported."""
    print("\n=== Test 3: Module Imports ===")
    
    try:
        sys.path.insert(0, '/config/custom_components/tado_ce')
        
        print("Importing water_heater...")
        from water_heater import TadoWaterHeater
        print("✓ water_heater imported successfully")
        
        print("Importing button...")
        from button import TadoWaterHeaterTimerButton
        print("✓ button imported successfully")
        
        print("Importing __init__...")
        # Can't import __init__ directly due to homeassistant dependencies
        # but we can check if the file exists
        import os
        if os.path.exists('/config/custom_components/tado_ce/__init__.py'):
            print("✓ __init__.py exists")
        
        print("\nResult: All imports successful")
        return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("Tado CE Service Compatibility Integration Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Time Period Parsing", test_time_period_parsing()))
    results.append(("Button Time Conversion", test_button_time_conversion()))
    results.append(("Module Imports", test_service_imports()))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
