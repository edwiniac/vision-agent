#!/usr/bin/env python3
"""Quick test script for VisionAgent."""

import sys
import os


def test_imports():
    """Test 1: Imports"""
    print("\n[Test 1] Testing imports...")
    try:
        from vision_agent import VisionAgent, VisionModel, ActionExecutor
        print("  ✅ Imports OK")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_api_key():
    """Test 2: API Key"""
    print("\n[Test 2] Checking API key...")
    if os.getenv('OPENAI_API_KEY'):
        print("  ✅ API key set")
        return True
    else:
        print("  ⚠️ OPENAI_API_KEY not set (vision features won't work)")
        return True  # Don't fail, just warn


def test_dry_run_actions():
    """Test 3: Dry run actions"""
    print("\n[Test 3] Testing dry-run actions...")
    try:
        from vision_agent.actions import ActionExecutor
        executor = ActionExecutor(dry_run=True)
        
        results = [
            executor.click(100, 100).success,
            executor.type_text("test").success,
            executor.scroll("down").success,
        ]
        
        if all(results):
            print("  ✅ Dry-run actions OK")
            return True
        else:
            print("  ❌ Some actions failed")
            return False
    except Exception as e:
        print(f"  ❌ Action test failed: {e}")
        return False


def test_models():
    """Test 4: Data models"""
    print("\n[Test 4] Testing data models...")
    try:
        from vision_agent.vision import ElementLocation, AnalysisResult
        from vision_agent.actions import ActionResult
        
        # Test ElementLocation
        el = ElementLocation(
            description="Test button",
            x=100, y=200,
            width=80, height=30,
            element_type="button",
            confidence=0.9
        )
        assert el.coordinates == (100, 200)
        assert el.center == (140, 215)
        
        # Test AnalysisResult
        result = AnalysisResult(
            description="Test description",
            elements=[el],
            text_content=["Hello"]
        )
        assert result.find_element("button") == el
        
        # Test ActionResult
        action = ActionResult(
            success=True,
            action="click",
            details="Clicked at (100, 200)"
        )
        assert action.success
        
        print("  ✅ Data models OK")
        return True
    except Exception as e:
        print(f"  ❌ Model test failed: {e}")
        return False


def test_agent_init():
    """Test 5: Agent initialization"""
    print("\n[Test 5] Testing agent init...")
    try:
        import os
        from vision_agent.actions import ActionExecutor
        
        # Test action executor (doesn't need API key)
        executor = ActionExecutor(dry_run=True)
        result = executor.click(100, 100)
        assert result.success
        
        # Only test full agent if API key is set
        if os.getenv('OPENAI_API_KEY'):
            from vision_agent import VisionAgent
            agent = VisionAgent(dry_run=True, verbose=False)
            result = agent.click(100, 100)
            assert result.success
            print("  ✅ Agent init OK (with vision)")
        else:
            print("  ✅ Agent init OK (action executor only, no API key)")
        
        return True
    except Exception as e:
        print(f"  ❌ Agent init failed: {e}")
        return False


def test_cli():
    """Test 6: CLI module"""
    print("\n[Test 6] Testing CLI module...")
    try:
        from vision_agent.cli import cli
        # Just test it imports
        print("  ✅ CLI module OK")
        return True
    except Exception as e:
        print(f"  ❌ CLI test failed: {e}")
        return False


def main():
    print("=" * 50)
    print("🧪 VisionAgent Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("API Key", test_api_key),
        ("Dry-Run Actions", test_dry_run_actions),
        ("Data Models", test_models),
        ("Agent Init", test_agent_init),
        ("CLI Module", test_cli),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
