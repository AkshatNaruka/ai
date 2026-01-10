#!/usr/bin/env python3
"""
Smoke tests for SECI AI Assistant (Jarvis)
Tests basic functionality without requiring heavy dependencies.
"""

import sys
import os
import subprocess
import json
from pathlib import Path


def print_test(name):
    """Print test name."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)


def print_ok(msg):
    """Print success message."""
    print(f"✓ {msg}")


def print_fail(msg):
    """Print failure message."""
    print(f"✗ {msg}")


def test_imports():
    """Test that core modules can be imported."""
    print_test("Import Core Modules")
    
    try:
        import seci
        print_ok("seci package imported")
    except ImportError as e:
        print_fail(f"Failed to import seci: {e}")
        return False
    
    try:
        from seci.config.config import SECIConfig
        print_ok("SECIConfig imported")
    except ImportError as e:
        print_fail(f"Failed to import SECIConfig: {e}")
        return False
    
    return True


def test_search_imports():
    """Test that search modules can be imported."""
    print_test("Import Search Modules")
    
    try:
        from seci.search import SearchEngine
        print_ok("SearchEngine imported")
    except ImportError as e:
        print_fail(f"Failed to import SearchEngine: {e}")
        return False
    
    try:
        from seci.scraper import WebScraper
        print_ok("WebScraper imported")
    except ImportError as e:
        print_fail(f"Failed to import WebScraper: {e}")
        return False
    
    try:
        from seci.context import ContextManager
        print_ok("ContextManager imported")
    except ImportError as e:
        print_fail(f"Failed to import ContextManager: {e}")
        return False
    
    return True


def test_config():
    """Test configuration loading."""
    print_test("Configuration")
    
    try:
        from seci.config.config import SECIConfig
        
        # Test default config
        config_path = Path("config/default.yaml")
        if config_path.exists():
            config = SECIConfig.from_yaml(str(config_path))
            print_ok(f"Loaded config from {config_path}")
        else:
            print_fail(f"Config file not found: {config_path}")
            return False
        
        # Check config attributes
        assert hasattr(config, 'model')
        assert hasattr(config, 'memory')
        print_ok("Config has expected attributes")
        
        return True
        
    except Exception as e:
        print_fail(f"Config test failed: {e}")
        return False


def test_jarvis_cli():
    """Test Jarvis CLI."""
    print_test("Jarvis CLI")
    
    try:
        # Test help command
        result = subprocess.run(
            [sys.executable, "jarvis.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_ok("jarvis.py --help works")
        else:
            print_fail(f"jarvis.py --help failed: {result.stderr}")
            return False
        
        # Test status command
        result = subprocess.run(
            [sys.executable, "jarvis.py", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_ok("jarvis.py status works")
        else:
            print_fail(f"jarvis.py status failed: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print_fail(f"Jarvis CLI test failed: {e}")
        return False


def test_install_script():
    """Test install script."""
    print_test("Install Script")
    
    try:
        # Test help command
        result = subprocess.run(
            [sys.executable, "install.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_ok("install.py --help works")
        else:
            print_fail(f"install.py --help failed: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print_fail(f"Install script test failed: {e}")
        return False


def test_cli_test_tool():
    """Test CLI test tool."""
    print_test("CLI Test Tool")
    
    try:
        # Test help command
        result = subprocess.run(
            [sys.executable, "cli_test.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_ok("cli_test.py --help works")
        else:
            print_fail(f"cli_test.py --help failed: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print_fail(f"CLI test tool test failed: {e}")
        return False


def test_file_structure():
    """Test that required files exist."""
    print_test("File Structure")
    
    required_files = [
        "README.md",
        "QUICKSTART.md",
        "requirements.txt",
        "requirements-minimal.txt",
        "setup.py",
        "install.py",
        "jarvis.py",
        "api.py",
        "cli_test.py",
        "config/default.yaml",
        "Dockerfile",
        "docker-compose.yml",
    ]
    
    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print_ok(f"{file} exists")
        else:
            print_fail(f"{file} missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SECI AI Assistant - Smoke Tests")
    print("="*60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Core Imports", test_imports),
        ("Search Imports", test_search_imports),
        ("Configuration", test_config),
        ("Install Script", test_install_script),
        ("Jarvis CLI", test_jarvis_cli),
        ("CLI Test Tool", test_cli_test_tool),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print_fail(f"Test {name} crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
