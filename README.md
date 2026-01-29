# 👁️ VisionAgent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/GPT--4V-Vision-green.svg)](https://openai.com/)

**AI that can see and interact with any UI.** Give it a screenshot, tell it what to do, and watch it work.

## 🎯 What Is This?

VisionAgent uses vision-language models (GPT-4V, Claude Vision) to:
1. **See** — Understand what's on screen
2. **Think** — Plan how to accomplish your goal
3. **Act** — Execute clicks, typing, scrolling

```
You: "Click the Submit button"

VisionAgent:
  📸 Analyzing screenshot...
  🔍 Found: Submit button at coordinates (847, 523)
  🖱️ Clicking at (847, 523)
  ✅ Done!
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 👁️ **Universal UI Understanding** | Works with any application — web, desktop, mobile |
| 🎯 **Natural Language Commands** | "Click the blue button", "Type my email in the login field" |
| 🖱️ **Full Interaction Suite** | Click, double-click, right-click, type, scroll, drag |
| 📸 **Screenshot Analysis** | Describe any UI, find elements, extract text |
| 🔄 **Multi-Step Automation** | Chain commands: "Log in, go to settings, change my name" |
| 🌐 **Browser Integration** | Special mode for web automation with Playwright |
| 🖥️ **Desktop Automation** | Control any desktop application via PyAutoGUI |

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/edwiniac/vision-agent.git
cd vision-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For desktop automation (optional)
pip install pyautogui

# For browser automation (optional)  
pip install playwright
playwright install chromium
```

### Set Up API Key

```bash
export OPENAI_API_KEY="your-key"
# Or for Claude Vision:
export ANTHROPIC_API_KEY="your-key"
```

### Basic Usage

```bash
# Analyze a screenshot
vision-agent analyze screenshot.png

# Find an element
vision-agent find "Submit button" --screenshot screenshot.png

# Execute an action (desktop)
vision-agent do "Click the Settings icon"

# Execute an action (browser)
vision-agent browse "Go to github.com and click Sign In"

# Interactive mode
vision-agent interactive
```

## 📖 Detailed Usage Guide

### 1. Screenshot Analysis

Understand what's on any screen:

```bash
$ vision-agent analyze screenshot.png

📸 Analyzing: screenshot.png

📝 Description:
This is a login page for GitHub. The page contains:
- GitHub logo at the top center
- "Sign in to GitHub" heading
- Username/email input field (currently empty)
- Password input field (currently empty)  
- "Forgot password?" link
- Green "Sign in" button
- "Create an account" link at the bottom

🎯 Interactive Elements Found:
1. [Input] Username field at (512, 280)
2. [Input] Password field at (512, 350)
3. [Link] "Forgot password?" at (512, 390)
4. [Button] "Sign in" at (512, 450)
5. [Link] "Create an account" at (512, 520)
```

### 2. Find Elements

Locate specific UI elements:

```bash
$ vision-agent find "Sign in button" --screenshot login.png

🔍 Searching for: "Sign in button"

✅ Found!
- Element: Green button labeled "Sign in"
- Location: (512, 450)
- Size: ~100x40 pixels
- Confidence: 95%

💡 To click this element:
   vision-agent click 512 450
```

### 3. Execute Actions

Perform actions on screen:

```bash
# Click at coordinates
$ vision-agent click 512 450

# Click by description (takes screenshot first)
$ vision-agent do "Click the Sign in button"

# Type text
$ vision-agent type "hello@email.com"

# Type into specific field
$ vision-agent do "Type 'mypassword' in the password field"

# Scroll
$ vision-agent scroll down
$ vision-agent scroll up --amount 500

# Complex action
$ vision-agent do "Right-click on the file icon and select Delete"
```

### 4. Multi-Step Automation

Chain multiple actions:

```bash
$ vision-agent automate "
1. Click the username field
2. Type 'edwin@example.com'
3. Click the password field  
4. Type 'mypassword'
5. Click the Sign in button
"

🤖 Executing automation sequence...

Step 1/5: Click the username field
  📸 Taking screenshot...
  🔍 Found username field at (512, 280)
  🖱️ Clicking...
  ✅ Done

Step 2/5: Type 'edwin@example.com'
  ⌨️ Typing...
  ✅ Done

Step 3/5: Click the password field
  📸 Taking screenshot...
  🔍 Found password field at (512, 350)
  🖱️ Clicking...
  ✅ Done

Step 4/5: Type 'mypassword'
  ⌨️ Typing...
  ✅ Done

Step 5/5: Click the Sign in button
  📸 Taking screenshot...
  🔍 Found Sign in button at (512, 450)
  🖱️ Clicking...
  ✅ Done

🎉 Automation complete! (5/5 steps succeeded)
```

### 5. Browser Mode

Special mode for web automation:

```bash
$ vision-agent browse "Go to amazon.com, search for 'laptop', and click the first result"

🌐 Starting browser automation...

Step 1: Navigate to amazon.com
  🌐 Opening https://amazon.com
  ✅ Page loaded

Step 2: Search for 'laptop'
  📸 Analyzing page...
  🔍 Found search box
  ⌨️ Typing 'laptop'
  🔍 Found search button
  🖱️ Clicking search
  ✅ Search complete

Step 3: Click the first result
  📸 Analyzing results page...
  🔍 Found first product result
  🖱️ Clicking...
  ✅ Done

🎉 Task complete!
```

### 6. Interactive Mode

Real-time control:

```bash
$ vision-agent interactive

👁️ VisionAgent Interactive Mode
Type commands or 'quit' to exit.

> screenshot
📸 Screenshot saved to: screenshot_001.png

> what do you see?
📝 I see a desktop with:
- Chrome browser open showing Gmail
- VS Code in the background
- Slack icon in the taskbar
- System tray showing 3:45 PM

> click the Slack icon
🔍 Found Slack icon in taskbar at (1250, 1060)
🖱️ Clicking...
✅ Done

> type "Hello team!"
⌨️ Typing...
✅ Done

> quit
Goodbye!
```

## 🧪 Testing Guide

### Test 1: Basic Import Test

```bash
cd vision-agent
python -c "from vision_agent import VisionAgent; print('✓ Import OK')"
```

### Test 2: Screenshot Analysis (No Actions)

```bash
# Take a screenshot manually or use:
python -c "
import pyautogui
pyautogui.screenshot('test_screenshot.png')
print('Screenshot saved!')
"

# Analyze it
vision-agent analyze test_screenshot.png
```

### Test 3: Element Finding

```bash
# Use any screenshot
vision-agent find "any button" --screenshot test_screenshot.png
```

### Test 4: Coordinate Click (Safe Test)

```bash
# This will just click at a coordinate
# Make sure nothing important is at 100,100!
vision-agent click 100 100 --dry-run
```

### Test 5: Full Automation Test

```bash
# Open a browser to google.com manually, then:
vision-agent do "Click the search box" --dry-run
```

### Test 6: Browser Mode Test

```bash
# Full browser test (creates its own browser)
vision-agent browse "Go to example.com and tell me what you see" --dry-run
```

### Test 7: Python API Test

```python
from vision_agent import VisionAgent

agent = VisionAgent()

# Test 1: Analyze an image
result = agent.analyze("screenshot.png")
print(result.description)

# Test 2: Find element (no action)
element = agent.find_element("Submit button", "screenshot.png")
print(f"Found at: {element.coordinates}")

# Test 3: Dry run action
agent.click(500, 500, dry_run=True)
```

## 🏗️ Architecture

```
vision-agent/
├── vision_agent/
│   ├── __init__.py
│   ├── core.py           # Main VisionAgent class
│   ├── vision.py         # Vision model integration (GPT-4V, Claude)
│   ├── actions.py        # Action executors (click, type, scroll)
│   ├── screenshot.py     # Screenshot capture utilities
│   ├── browser.py        # Playwright browser automation
│   └── cli.py            # Command-line interface
├── tests/
│   ├── test_vision.py
│   ├── test_actions.py
│   └── test_integration.py
├── examples/
│   ├── login_automation.py
│   ├── form_filling.py
│   └── web_scraping.py
├── requirements.txt
└── README.md
```

## 🔧 Configuration

```yaml
# config.yaml
vision:
  provider: openai  # openai or anthropic
  model: gpt-4o     # gpt-4o, gpt-4-vision-preview, claude-3-opus
  
actions:
  click_delay: 0.5      # Seconds between actions
  type_delay: 0.05      # Seconds between keystrokes
  screenshot_dir: ./screenshots
  
safety:
  dry_run: false        # If true, don't execute actions
  confirm_actions: true # Ask before executing
  safe_zones: []        # Regions to never click
```

## 🔌 Python API

```python
from vision_agent import VisionAgent

# Initialize
agent = VisionAgent(
    provider="openai",      # or "anthropic"
    model="gpt-4o",
    dry_run=False
)

# Analyze screenshot
analysis = agent.analyze("screenshot.png")
print(analysis.description)
print(analysis.elements)

# Find element
element = agent.find_element(
    description="Login button",
    screenshot="page.png"
)
print(f"Found at: {element.x}, {element.y}")

# Execute action
agent.click(element.x, element.y)
agent.type_text("hello world")
agent.scroll("down", amount=300)

# High-level command
agent.do("Click the submit button and wait for the page to load")

# Multi-step automation
agent.automate([
    "Open Chrome",
    "Go to gmail.com",
    "Click compose",
    "Type 'Hello' in the subject"
])

# Browser mode
with agent.browser() as browser:
    browser.goto("https://github.com")
    browser.do("Click Sign In")
    browser.do("Type 'username' in the username field")
```

## ⚠️ Safety Features

1. **Dry Run Mode** — Preview actions without executing
2. **Confirmation Prompts** — Ask before clicking/typing
3. **Safe Zones** — Define regions that should never be clicked
4. **Action Logging** — Full audit trail of all actions
5. **Rate Limiting** — Prevent runaway automation

## 📊 Supported Vision Models

| Model | Provider | Quality | Speed | Cost |
|-------|----------|---------|-------|------|
| gpt-4o | OpenAI | ⭐⭐⭐⭐⭐ | Fast | $$ |
| gpt-4-vision-preview | OpenAI | ⭐⭐⭐⭐ | Medium | $$$ |
| claude-3-opus | Anthropic | ⭐⭐⭐⭐⭐ | Medium | $$$ |
| claude-3-sonnet | Anthropic | ⭐⭐⭐⭐ | Fast | $$ |

## 🗺️ Roadmap

- [x] Screenshot analysis
- [x] Element finding
- [x] Click/type/scroll actions
- [x] Multi-step automation
- [x] Browser integration
- [ ] Mobile device support (ADB)
- [ ] OCR fallback for text extraction
- [ ] Recording mode (watch & learn)
- [ ] Visual regression testing

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

**See. Think. Act.** Automate anything with AI vision.
