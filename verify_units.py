from utils.logic_engine import PricingEngine

def test_conversions():
    # Test cases: (value, unit, expected_meters)
    tests = [
        (1000, 'mm', 1.0),
        (1, 'm', 1.0),
        (100, 'cm', 1.0),
        (1, 'ft', 0.3048),
        (12, 'in', 0.3048),
        (1, 'in', 0.0254)
    ]
    
    print("Running Unit Conversion Tests...")
    all_passed = True
    for val, unit, expected in tests:
        result = PricingEngine.convert_to_meters(val, unit)
        # Use small epsilon for float comparison
        if abs(result - expected) < 1e-9:
            print(f"[PASS] {val} {unit} -> {result} m")
        else:
            print(f"[FAIL] {val} {unit} -> {result} m (Expected {expected})")
            all_passed = False
            
    if all_passed:
        print("\nAll unit conversion tests passed!")
    else:
        print("\nSome tests failed.")
        exit(1)

if __name__ == "__main__":
    test_conversions()
