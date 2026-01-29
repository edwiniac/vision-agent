"""Action executors for interacting with the screen."""

import time
from dataclasses import dataclass
from typing import Optional, Literal
from pathlib import Path

# Try to import automation libraries
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class ActionResult:
    """Result of executing an action."""
    success: bool
    action: str
    details: str
    error: Optional[str] = None


class ActionExecutor:
    """Executes UI actions like clicking, typing, and scrolling."""
    
    def __init__(
        self,
        click_delay: float = 0.3,
        type_delay: float = 0.02,
        dry_run: bool = False,
        confirm: bool = False
    ):
        self.click_delay = click_delay
        self.type_delay = type_delay
        self.dry_run = dry_run
        self.confirm = confirm
        
        if not PYAUTOGUI_AVAILABLE and not dry_run:
            print("Warning: pyautogui not installed. Actions will be simulated.")
            self.dry_run = True
        
        # Configure pyautogui safety
        if PYAUTOGUI_AVAILABLE:
            pyautogui.FAILSAFE = True  # Move mouse to corner to abort
            pyautogui.PAUSE = 0.1
    
    def _confirm_action(self, action: str) -> bool:
        """Ask user to confirm action."""
        if not self.confirm:
            return True
        response = input(f"Execute '{action}'? [y/N]: ")
        return response.lower() in ("y", "yes")
    
    def screenshot(self, save_path: Optional[str] = None) -> Optional[str]:
        """Take a screenshot."""
        if not PYAUTOGUI_AVAILABLE:
            return None
        
        if save_path is None:
            save_path = f"screenshot_{int(time.time())}.png"
        
        if self.dry_run:
            print(f"[DRY RUN] Would save screenshot to: {save_path}")
            return save_path
        
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        return save_path
    
    def click(
        self,
        x: int,
        y: int,
        button: Literal["left", "right", "middle"] = "left",
        clicks: int = 1
    ) -> ActionResult:
        """Click at coordinates."""
        action = f"click({x}, {y}, button={button}, clicks={clicks})"
        
        if self.dry_run:
            return ActionResult(
                success=True,
                action=action,
                details=f"[DRY RUN] Would click at ({x}, {y})"
            )
        
        if not self._confirm_action(action):
            return ActionResult(
                success=False,
                action=action,
                details="Action cancelled by user"
            )
        
        try:
            pyautogui.click(x, y, clicks=clicks, button=button)
            time.sleep(self.click_delay)
            return ActionResult(
                success=True,
                action=action,
                details=f"Clicked at ({x}, {y})"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=action,
                details="Click failed",
                error=str(e)
            )
    
    def double_click(self, x: int, y: int) -> ActionResult:
        """Double-click at coordinates."""
        return self.click(x, y, clicks=2)
    
    def right_click(self, x: int, y: int) -> ActionResult:
        """Right-click at coordinates."""
        return self.click(x, y, button="right")
    
    def type_text(
        self,
        text: str,
        interval: Optional[float] = None
    ) -> ActionResult:
        """Type text."""
        action = f"type({repr(text[:30])}{'...' if len(text) > 30 else ''})"
        interval = interval or self.type_delay
        
        if self.dry_run:
            return ActionResult(
                success=True,
                action=action,
                details=f"[DRY RUN] Would type: {text[:50]}..."
            )
        
        if not self._confirm_action(action):
            return ActionResult(
                success=False,
                action=action,
                details="Action cancelled by user"
            )
        
        try:
            pyautogui.typewrite(text, interval=interval)
            return ActionResult(
                success=True,
                action=action,
                details=f"Typed {len(text)} characters"
            )
        except Exception as e:
            # Fall back to write for special characters
            try:
                pyautogui.write(text)
                return ActionResult(
                    success=True,
                    action=action,
                    details=f"Typed {len(text)} characters (write mode)"
                )
            except Exception as e2:
                return ActionResult(
                    success=False,
                    action=action,
                    details="Type failed",
                    error=str(e2)
                )
    
    def press_key(self, key: str) -> ActionResult:
        """Press a keyboard key."""
        action = f"press({key})"
        
        if self.dry_run:
            return ActionResult(
                success=True,
                action=action,
                details=f"[DRY RUN] Would press: {key}"
            )
        
        try:
            pyautogui.press(key)
            return ActionResult(
                success=True,
                action=action,
                details=f"Pressed {key}"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=action,
                details="Key press failed",
                error=str(e)
            )
    
    def hotkey(self, *keys: str) -> ActionResult:
        """Press a key combination."""
        action = f"hotkey({', '.join(keys)})"
        
        if self.dry_run:
            return ActionResult(
                success=True,
                action=action,
                details=f"[DRY RUN] Would press: {'+'.join(keys)}"
            )
        
        try:
            pyautogui.hotkey(*keys)
            return ActionResult(
                success=True,
                action=action,
                details=f"Pressed {'+'.join(keys)}"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=action,
                details="Hotkey failed",
                error=str(e)
            )
    
    def scroll(
        self,
        direction: Literal["up", "down", "left", "right"] = "down",
        amount: int = 3
    ) -> ActionResult:
        """Scroll the screen."""
        action = f"scroll({direction}, {amount})"
        
        if self.dry_run:
            return ActionResult(
                success=True,
                action=action,
                details=f"[DRY RUN] Would scroll {direction} by {amount}"
            )
        
        try:
            if direction == "up":
                pyautogui.scroll(amount)
            elif direction == "down":
                pyautogui.scroll(-amount)
            elif direction == "left":
                pyautogui.hscroll(-amount)
            elif direction == "right":
                pyautogui.hscroll(amount)
            
            return ActionResult(
                success=True,
                action=action,
                details=f"Scrolled {direction} by {amount}"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=action,
                details="Scroll failed",
                error=str(e)
            )
    
    def move_to(self, x: int, y: int, duration: float = 0.2) -> ActionResult:
        """Move mouse to coordinates."""
        action = f"move_to({x}, {y})"
        
        if self.dry_run:
            return ActionResult(
                success=True,
                action=action,
                details=f"[DRY RUN] Would move to ({x}, {y})"
            )
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return ActionResult(
                success=True,
                action=action,
                details=f"Moved to ({x}, {y})"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=action,
                details="Move failed",
                error=str(e)
            )
    
    def drag_to(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5
    ) -> ActionResult:
        """Drag from one point to another."""
        action = f"drag({start_x}, {start_y}) -> ({end_x}, {end_y})"
        
        if self.dry_run:
            return ActionResult(
                success=True,
                action=action,
                details=f"[DRY RUN] Would drag from ({start_x}, {start_y}) to ({end_x}, {end_y})"
            )
        
        try:
            pyautogui.moveTo(start_x, start_y)
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
            return ActionResult(
                success=True,
                action=action,
                details=f"Dragged to ({end_x}, {end_y})"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=action,
                details="Drag failed",
                error=str(e)
            )
    
    def wait(self, seconds: float) -> ActionResult:
        """Wait for a specified time."""
        action = f"wait({seconds}s)"
        
        if self.dry_run:
            return ActionResult(
                success=True,
                action=action,
                details=f"[DRY RUN] Would wait {seconds}s"
            )
        
        time.sleep(seconds)
        return ActionResult(
            success=True,
            action=action,
            details=f"Waited {seconds}s"
        )
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get screen dimensions."""
        if PYAUTOGUI_AVAILABLE:
            return pyautogui.size()
        return (1920, 1080)  # Default fallback
    
    def get_mouse_position(self) -> tuple[int, int]:
        """Get current mouse position."""
        if PYAUTOGUI_AVAILABLE:
            return pyautogui.position()
        return (0, 0)
