"""Core VisionAgent class that combines vision and actions."""

import time
from pathlib import Path
from typing import Optional, Union, List
from dataclasses import dataclass

from .vision import VisionModel, AnalysisResult, ElementLocation
from .actions import ActionExecutor, ActionResult


@dataclass
class StepResult:
    """Result of executing a single step."""
    step_number: int
    command: str
    success: bool
    action_result: Optional[ActionResult] = None
    element_found: Optional[ElementLocation] = None
    error: Optional[str] = None


@dataclass
class AutomationResult:
    """Result of a multi-step automation."""
    success: bool
    total_steps: int
    completed_steps: int
    steps: List[StepResult]
    duration_seconds: float


class VisionAgent:
    """AI agent that can see and interact with any UI."""
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4o",
        dry_run: bool = False,
        confirm: bool = False,
        verbose: bool = True
    ):
        self.vision = VisionModel(provider=provider, model=model)
        self.actions = ActionExecutor(dry_run=dry_run, confirm=confirm)
        self.dry_run = dry_run
        self.verbose = verbose
        self._screenshot_counter = 0
    
    def _log(self, message: str):
        """Print message if verbose mode is on."""
        if self.verbose:
            print(message)
    
    def _take_screenshot(self) -> str:
        """Take and save a screenshot."""
        self._screenshot_counter += 1
        path = f"va_screenshot_{self._screenshot_counter:03d}.png"
        self.actions.screenshot(path)
        return path
    
    def analyze(self, image_path: Union[str, Path]) -> AnalysisResult:
        """Analyze a screenshot and describe its contents."""
        self._log(f"📸 Analyzing: {image_path}")
        result = self.vision.analyze(image_path)
        self._log(f"📝 Found {len(result.elements)} elements")
        return result
    
    def find_element(
        self,
        description: str,
        image_path: Optional[Union[str, Path]] = None
    ) -> Optional[ElementLocation]:
        """Find a specific element on screen."""
        if image_path is None:
            self._log("📸 Taking screenshot...")
            image_path = self._take_screenshot()
        
        self._log(f"🔍 Searching for: {description}")
        element = self.vision.find_element(description, image_path)
        
        if element:
            self._log(f"✅ Found at ({element.x}, {element.y})")
        else:
            self._log("❌ Element not found")
        
        return element
    
    def click(self, x: int, y: int, **kwargs) -> ActionResult:
        """Click at coordinates."""
        self._log(f"🖱️ Clicking at ({x}, {y})")
        return self.actions.click(x, y, **kwargs)
    
    def type_text(self, text: str, **kwargs) -> ActionResult:
        """Type text."""
        self._log(f"⌨️ Typing: {text[:30]}{'...' if len(text) > 30 else ''}")
        return self.actions.type_text(text, **kwargs)
    
    def scroll(self, direction: str = "down", amount: int = 3) -> ActionResult:
        """Scroll the screen."""
        self._log(f"📜 Scrolling {direction}")
        return self.actions.scroll(direction, amount)
    
    def do(self, command: str, image_path: Optional[str] = None) -> ActionResult:
        """Execute a natural language command."""
        self._log(f"🤖 Command: {command}")
        
        # Take screenshot if not provided
        if image_path is None:
            self._log("📸 Taking screenshot...")
            image_path = self._take_screenshot()
        
        # Parse the command
        command_lower = command.lower()
        
        # Simple command parsing
        if command_lower.startswith("click"):
            # Try to find element to click
            target = command.replace("click", "").replace("Click", "").strip()
            if target:
                element = self.find_element(target, image_path)
                if element:
                    return self.click(element.x, element.y)
                else:
                    return ActionResult(
                        success=False,
                        action=command,
                        details=f"Could not find: {target}",
                        error="Element not found"
                    )
        
        elif "type" in command_lower or "enter" in command_lower:
            # Extract text to type
            import re
            match = re.search(r"['\"](.+?)['\"]", command)
            if match:
                text = match.group(1)
                return self.type_text(text)
        
        elif "scroll" in command_lower:
            if "up" in command_lower:
                return self.scroll("up")
            else:
                return self.scroll("down")
        
        # For complex commands, use vision model to plan
        self._log("🧠 Planning actions...")
        steps = self.vision.plan_action(command, image_path)
        
        if not steps:
            return ActionResult(
                success=False,
                action=command,
                details="Could not plan actions for this command",
                error="Planning failed"
            )
        
        # Execute first step
        step = steps[0]
        action = step.get("action", "")
        
        if action == "click":
            x = step.get("x")
            y = step.get("y")
            if x is not None and y is not None:
                return self.click(x, y)
            else:
                # Find element
                target = step.get("target", "")
                element = self.find_element(target, image_path)
                if element:
                    return self.click(element.x, element.y)
        
        elif action == "type":
            text = step.get("value", "")
            return self.type_text(text)
        
        elif action == "scroll":
            direction = step.get("value", "down")
            return self.scroll(direction)
        
        return ActionResult(
            success=False,
            action=command,
            details=f"Unknown action: {action}",
            error="Unknown action"
        )
    
    def automate(self, commands: Union[str, List[str]]) -> AutomationResult:
        """Execute multiple commands in sequence."""
        start_time = time.time()
        
        # Parse commands
        if isinstance(commands, str):
            # Split by newlines and numbered items
            import re
            commands = re.split(r'\n\d+\.\s*|\n-\s*|\n', commands)
            commands = [c.strip() for c in commands if c.strip()]
        
        self._log(f"🤖 Starting automation: {len(commands)} steps")
        
        results = []
        success_count = 0
        
        for i, command in enumerate(commands, 1):
            self._log(f"\n--- Step {i}/{len(commands)}: {command} ---")
            
            try:
                # Take fresh screenshot for each step
                screenshot = self._take_screenshot()
                action_result = self.do(command, screenshot)
                
                step_result = StepResult(
                    step_number=i,
                    command=command,
                    success=action_result.success,
                    action_result=action_result,
                )
                
                if action_result.success:
                    success_count += 1
                    self._log(f"✅ Step {i} complete")
                else:
                    self._log(f"❌ Step {i} failed: {action_result.error}")
                
            except Exception as e:
                step_result = StepResult(
                    step_number=i,
                    command=command,
                    success=False,
                    error=str(e)
                )
                self._log(f"❌ Step {i} error: {e}")
            
            results.append(step_result)
            
            # Small delay between steps
            time.sleep(0.5)
        
        duration = time.time() - start_time
        all_success = success_count == len(commands)
        
        self._log(f"\n🎉 Automation {'complete' if all_success else 'finished with errors'}!")
        self._log(f"   {success_count}/{len(commands)} steps succeeded")
        self._log(f"   Duration: {duration:.1f}s")
        
        return AutomationResult(
            success=all_success,
            total_steps=len(commands),
            completed_steps=success_count,
            steps=results,
            duration_seconds=duration,
        )
    
    def interactive(self):
        """Run in interactive mode."""
        print("👁️ VisionAgent Interactive Mode")
        print("Commands: 'screenshot', 'analyze', 'find <element>', 'click <x> <y>', 'type <text>', 'do <command>', 'quit'")
        print()
        
        while True:
            try:
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break
                
                if user_input.lower() == "screenshot":
                    path = self._take_screenshot()
                    print(f"📸 Saved: {path}")
                
                elif user_input.lower().startswith("analyze"):
                    parts = user_input.split(maxsplit=1)
                    path = parts[1] if len(parts) > 1 else self._take_screenshot()
                    result = self.analyze(path)
                    print(f"\n{result.description}\n")
                    for el in result.elements[:5]:
                        print(f"  - [{el.element_type}] {el.description} at ({el.x}, {el.y})")
                
                elif user_input.lower().startswith("find "):
                    target = user_input[5:]
                    element = self.find_element(target)
                    if element:
                        print(f"Found: {element.description} at ({element.x}, {element.y})")
                
                elif user_input.lower().startswith("click "):
                    parts = user_input.split()
                    if len(parts) >= 3:
                        x, y = int(parts[1]), int(parts[2])
                        self.click(x, y)
                
                elif user_input.lower().startswith("type "):
                    text = user_input[5:]
                    self.type_text(text)
                
                elif user_input.lower().startswith("do "):
                    command = user_input[3:]
                    self.do(command)
                
                else:
                    # Treat as a natural command
                    self.do(user_input)
            
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
