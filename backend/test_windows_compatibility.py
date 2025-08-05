#!/usr/bin/env python3
"""
Simple test to verify platform marker logic for Windows uvloop compatibility.
This test doesn't require installing dependencies and can verify the fix.
"""

import sys

def test_platform_detection():
    """Test platform detection logic used in requirements.txt."""
    print("Platform Detection Test")
    print("=" * 30)
    
    current_platform = sys.platform
    print(f"Current platform: {current_platform}")
    
    # Test our condition: uvloop==0.21.0; sys_platform != "win32"
    should_install_uvloop = sys.platform != "win32"
    print(f"Should install uvloop on this platform: {should_install_uvloop}")
    
    # Test for different platforms
    test_platforms = ["linux", "darwin", "win32", "cygwin"]
    print("\nPlatform compatibility test:")
    for platform in test_platforms:
        would_install = platform != "win32"
        status = "✓" if would_install else "✗"
        print(f"  {platform}: {status} {'Install uvloop' if would_install else 'Skip uvloop (Windows compatible)'}")
    
    return True

def test_requirements_syntax():
    """Test that our requirements.txt line has valid syntax."""
    print("\nRequirements Syntax Test")
    print("=" * 30)
    
    # Read the requirements.txt file
    try:
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
        
        uvloop_line = None
        for line in lines:
            if line.strip().startswith("uvloop"):
                uvloop_line = line.strip()
                break
        
        if not uvloop_line:
            print("✗ uvloop line not found in requirements.txt")
            return False
        
        print(f"Found uvloop line: {uvloop_line}")
        
        # Check if it has the platform marker
        if "; sys_platform != \"win32\"" in uvloop_line:
            print("✓ Platform marker found and correctly formatted")
            return True
        else:
            print("✗ Platform marker missing or incorrectly formatted")
            return False
            
    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")
        return False

def test_windows_requirements():
    """Test that Windows requirements file exists and is valid."""
    print("\nWindows Requirements File Test")
    print("=" * 35)
    
    try:
        with open("requirements-windows.txt", "r") as f:
            lines = f.readlines()
        
        # Check that uvloop is not in the Windows requirements (excluding comments)
        has_uvloop = any("uvloop" in line and not line.strip().startswith("#") for line in lines)
        
        if has_uvloop:
            print("✗ uvloop found in Windows requirements file")
            return False
        else:
            print("✓ uvloop correctly excluded from Windows requirements")
        
        # Check that other essential packages are still there
        essential_packages = ["fastapi", "uvicorn", "pydantic"]
        missing_packages = []
        
        for package in essential_packages:
            if not any(package in line.lower() for line in lines):
                missing_packages.append(package)
        
        if missing_packages:
            print(f"✗ Missing essential packages: {missing_packages}")
            return False
        else:
            print("✓ All essential packages present in Windows requirements")
        
        print(f"✓ Windows requirements file has {len(lines)} packages")
        return True
        
    except Exception as e:
        print(f"✗ Error reading requirements-windows.txt: {e}")
        return False

def main():
    """Run all tests."""
    print("EvolveUI Windows Compatibility Tests")
    print("=" * 40)
    print(f"Python version: {sys.version}")
    print()
    
    tests = [
        test_platform_detection,
        test_requirements_syntax,
        test_windows_requirements,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"✗ Test error: {e}")
            print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Windows compatibility implemented correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())