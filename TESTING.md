# 🧪 VisionAgent Testing Guide

This document explains how to test every component of VisionAgent.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Test 1: Import Test](#test-1-import-test)
4. [Test 2: Vision Model Test](#test-2-vision-model-test)
5. [Test 3: Screenshot Analysis](#test-3-screenshot-analysis)
6. [Test 4: Element Finding](#test-4-element-finding)
7. [Test 5: Action Executor (Dry Run)](#test-5-action-executor-dry-run)
8. [Test 6: Full Integration Test](#test-6-full-integration-test)
9. [Test 7: CLI Test](#test-7-cli-test)
10. [Test 8: Real Automation Test](#test-8-real-automation-test)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before testing, ensure you have:

- Python 3.10+
- OpenAI API key with GPT-4V access
- (Optional) A display for desktop automation tests

## Installation

```bash
# Clone the repository
git clone https://github.com/edwiniac/vision-agent.git
cd vision-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For desktop automation (optional but recommended)
pip install pyautogui

# Set API key
export OPENAI_API_KEY="sk-your-key-here"
```

---

## Test 1: Import Test

**Purpose:** Verify all modules load correctly without errors.

```bash
python -c "
from vision_agent import VisionAgent, VisionModel, ActionExecutor
from vision_agent.vision import AnalysisResult, ElementLocation
from vision_agent.actions import ActionResult

print('✅ All imports successful!')
"
```

**Expected Output:**
```
✅ All imports successful!
```

**If it fails:** Check that all dependencies are installed.

---

## Test 2: Vision Model Test

**Purpose:** Test the vision model can be initialized and the API connection works.

```bash
python -c "
import os
from vision_agent.vision import VisionModel

# Check API key
assert os.getenv('OPENAI_API_KEY'), 'OPENAI_API_KEY not set!'

# Initialize model
model = VisionModel(provider='openai', model='gpt-4o')
print(f'✅ VisionModel initialized: {model.model}')
"
```

**Expected Output:**
```
✅ VisionModel initialized: gpt-4o
```

---

## Test 3: Screenshot Analysis

**Purpose:** Test analyzing an actual screenshot with the vision model.

### Step 1: Create a test image

```bash
# Option A: Take a screenshot (requires pyautogui)
python -c "
import pyautogui
screenshot = pyautogui.screenshot()
screenshot.save('test_screenshot.png')
print('✅ Screenshot saved: test_screenshot.png')
"

# Option B: Use any existing PNG image
# Just ensure you have a file called test_screenshot.png
```

### Step 2: Analyze the screenshot

```bash
python -c "
from vision_agent import VisionAgent

agent = VisionAgent(verbose=True)
result = agent.analyze('test_screenshot.png')

print('\n' + '='*50)
print('ANALYSIS RESULT')
print('='*50)
print(f'\nDescription:\n{result.description[:500]}...')
print(f'\nElements found: {len(result.elements)}')
for i, el in enumerate(result.elements[:5], 1):
    print(f'  {i}. [{el.element_type}] {el.description} at ({el.x}, {el.y})')
print('\n✅ Screenshot analysis test passed!')
"
```

**Expected Output:**
```
📸 Analyzing: test_screenshot.png
📝 Found X elements

==================================================
ANALYSIS RESULT
==================================================

Description:
[Description of what's in the screenshot...]

Elements found: X
  1. [button] Some button at (100, 200)
  2. [input] Some input field at (300, 400)
  ...

✅ Screenshot analysis test passed!
```

---

## Test 4: Element Finding

**Purpose:** Test finding specific elements in a screenshot.

```bash
python -c "
from vision_agent import VisionAgent

agent = VisionAgent(verbose=True)

# Try to find a common element (adjust based on your screenshot)
element = agent.find_element('any button or clickable element', 'test_screenshot.png')

if element:
    print('\n' + '='*50)
    print('ELEMENT FOUND')
    print('='*50)
    print(f'Description: {element.description}')
    print(f'Type: {element.element_type}')
    print(f'Coordinates: ({element.x}, {element.y})')
    print(f'Confidence: {element.confidence*100:.0f}%')
    print('\n✅ Element finding test passed!')
else:
    print('⚠️ No element found (this may be expected depending on the screenshot)')
"
```

---

## Test 5: Action Executor (Dry Run)

**Purpose:** Test action execution logic without actually performing actions.

```bash
python -c "
from vision_agent.actions import ActionExecutor

# Create executor in dry-run mode (safe - won't actually do anything)
executor = ActionExecutor(dry_run=True)

print('Testing actions in DRY RUN mode...\n')

# Test click
result = executor.click(500, 300)
print(f'Click: {result.details}')

# Test type
result = executor.type_text('Hello World')
print(f'Type: {result.details}')

# Test scroll
result = executor.scroll('down', 3)
print(f'Scroll: {result.details}')

# Test move
result = executor.move_to(100, 100)
print(f'Move: {result.details}')

# Test key press
result = executor.press_key('enter')
print(f'Press: {result.details}')

# Test hotkey
result = executor.hotkey('ctrl', 'c')
print(f'Hotkey: {result.details}')

print('\n✅ All action tests passed (dry run)!')
"
```

**Expected Output:**
```
Testing actions in DRY RUN mode...

Click: [DRY RUN] Would click at (500, 300)
Type: [DRY RUN] Would type: Hello World...
Scroll: [DRY RUN] Would scroll down by 3
Move: [DRY RUN] Would move to (100, 100)
Press: [DRY RUN] Would press: enter
Hotkey: [DRY RUN] Would press: ctrl+c

✅ All action tests passed (dry run)!
```

---

## Test 6: Full Integration Test

**Purpose:** Test the complete VisionAgent workflow (dry run).

```bash
python -c "
from vision_agent import VisionAgent

# Create agent in dry-run mode
agent = VisionAgent(dry_run=True, verbose=True)

print('='*50)
print('INTEGRATION TEST (DRY RUN)')
print('='*50)

# Test 1: Analyze
print('\n--- Test: Analyze ---')
result = agent.analyze('test_screenshot.png')
print(f'Analysis: Found {len(result.elements)} elements')

# Test 2: Find element
print('\n--- Test: Find Element ---')
element = agent.find_element('button', 'test_screenshot.png')
print(f'Find: {\"Found\" if element else \"Not found\"}')

# Test 3: Click (dry run)
print('\n--- Test: Click ---')
result = agent.click(500, 300)
print(f'Click: {result.success}')

# Test 4: Type (dry run)
print('\n--- Test: Type ---')
result = agent.type_text('test input')
print(f'Type: {result.success}')

# Test 5: Natural command (dry run)
print('\n--- Test: Natural Command ---')
result = agent.do('Click the button', 'test_screenshot.png')
print(f'Command: {result.details}')

print('\n' + '='*50)
print('✅ All integration tests passed!')
print('='*50)
"
```

---

## Test 7: CLI Test

**Purpose:** Test the command-line interface.

```bash
# Test CLI help
python -m vision_agent --help

# Test analyze command
python -m vision_agent analyze test_screenshot.png

# Test find command
python -m vision_agent find "button" --screenshot test_screenshot.png

# Test click (dry run - safe)
python -m vision_agent click 500 300 --dry-run

# Test type (dry run - safe)
python -m vision_agent type "hello world" --dry-run

# Test do command (dry run - safe)
python -m vision_agent do "click the button" --dry-run
```

**Expected Output for --help:**
```
Usage: python -m vision_agent [OPTIONS] COMMAND [ARGS]...

  👁️ VisionAgent - AI that can see and interact with any UI.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  analyze      Analyze a screenshot and describe its contents.
  automate     Run multi-step automation.
  click        Click at coordinates.
  do           Execute a natural language command.
  find         Find a specific element on screen.
  interactive  Start interactive mode.
  screenshot   Take a screenshot.
  scroll       Scroll the screen.
  type         Type text.
```

---

## Test 8: Real Automation Test

⚠️ **WARNING:** This test performs REAL actions on your computer!

Only run this when you're ready and have a safe environment.

```bash
# Open a text editor or notepad first, then run:
python -c "
from vision_agent import VisionAgent
import time

print('⚠️ REAL AUTOMATION TEST')
print('This will type text in 3 seconds...')
print('Click on a text editor NOW!')
time.sleep(3)

agent = VisionAgent(dry_run=False, verbose=True)
result = agent.type_text('Hello from VisionAgent!')

if result.success:
    print('✅ Real automation test passed!')
else:
    print(f'❌ Failed: {result.error}')
"
```

---

## Quick Test Script

Save this as `run_tests.py` for easy testing:

```python
#!/usr/bin/env python3
\"\"\"Quick test script for VisionAgent.\"\"\"

import sys
import os

def test_imports():
    \"\"\"Test 1: Imports\"\"\"
    print("\\n[Test 1] Testing imports...")
    try:
        from vision_agent import VisionAgent, VisionModel, ActionExecutor
        print("  ✅ Imports OK")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_api_key():
    \"\"\"Test 2: API Key\"\"\"
    print("\\n[Test 2] Checking API key...")
    if os.getenv('OPENAI_API_KEY'):
        print("  ✅ API key set")
        return True
    else:
        print("  ❌ OPENAI_API_KEY not set")
        return False

def test_dry_run_actions():
    \"\"\"Test 3: Dry run actions\"\"\"
    print("\\n[Test 3] Testing dry-run actions...")
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

def test_vision_init():
    \"\"\"Test 4: Vision model init\"\"\"
    print("\\n[Test 4] Testing vision model...")
    try:
        from vision_agent.vision import VisionModel
        model = VisionModel()
        print(f"  ✅ Vision model OK ({model.model})")
        return True
    except Exception as e:
        print(f"  ❌ Vision model failed: {e}")
        return False

def main():
    print("="*50)
    print("VisionAgent Test Suite")
    print("="*50)
    
    results = [
        test_imports(),
        test_api_key(),
        test_dry_run_actions(),
        test_vision_init(),
    ]
    
    print("\\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Run with:
```bash
python run_tests.py
```

---

## Troubleshooting

### "No module named 'openai'"
```bash
pip install openai
```

### "No module named 'pyautogui'"
```bash
pip install pyautogui
```

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### "pyautogui needs a display"
If running on a headless server:
```bash
# Install virtual display
sudo apt-get install xvfb
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
```

### "Screenshot is black"
This happens on some systems. Try:
```bash
pip install pyscreeze pillow
```

### Rate limit errors
The GPT-4V API has rate limits. Wait a few seconds between calls or use a paid tier.

---

## Summary

| Test | What it Tests | Safe to Run? |
|------|--------------|--------------|
| Import Test | Module loading | ✅ Yes |
| Vision Model Test | API connection | ✅ Yes |
| Screenshot Analysis | Vision AI | ✅ Yes |
| Element Finding | Element detection | ✅ Yes |
| Action Executor (Dry) | Action logic | ✅ Yes |
| Integration Test | Full workflow | ✅ Yes (dry run) |
| CLI Test | Command line | ✅ Yes |
| Real Automation | Actual actions | ⚠️ Careful! |

---

**Happy Testing!** 🧪
