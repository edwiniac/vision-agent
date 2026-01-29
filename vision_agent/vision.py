"""Vision model integration for analyzing screenshots."""

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

from openai import OpenAI


@dataclass
class ElementLocation:
    """Location of a UI element."""
    description: str
    x: int
    y: int
    width: Optional[int] = None
    height: Optional[int] = None
    element_type: str = "unknown"  # button, input, link, text, image, etc.
    confidence: float = 0.0
    
    @property
    def coordinates(self) -> tuple[int, int]:
        return (self.x, self.y)
    
    @property
    def center(self) -> tuple[int, int]:
        if self.width and self.height:
            return (self.x + self.width // 2, self.y + self.height // 2)
        return (self.x, self.y)


@dataclass
class AnalysisResult:
    """Result of analyzing a screenshot."""
    description: str
    elements: list[ElementLocation] = field(default_factory=list)
    text_content: list[str] = field(default_factory=list)
    raw_response: str = ""
    
    def find_element(self, description: str) -> Optional[ElementLocation]:
        """Find element matching description."""
        description_lower = description.lower()
        for element in self.elements:
            if description_lower in element.description.lower():
                return element
        return None


class VisionModel:
    """Interface for vision-language models."""
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4o",
        client: Optional[OpenAI] = None
    ):
        self.provider = provider
        self.model = model
        
        if provider == "openai":
            self.client = client or OpenAI()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _encode_image(self, image_path: Union[str, Path]) -> str:
        """Encode image to base64."""
        path = Path(image_path)
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _get_image_media_type(self, image_path: Union[str, Path]) -> str:
        """Get media type from file extension."""
        ext = Path(image_path).suffix.lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return media_types.get(ext, "image/png")
    
    def analyze(self, image_path: Union[str, Path]) -> AnalysisResult:
        """Analyze a screenshot and describe its contents."""
        image_data = self._encode_image(image_path)
        media_type = self._get_image_media_type(image_path)
        
        system_prompt = """You are a UI analysis expert. Analyze the screenshot and provide:

1. A detailed description of what's visible on screen
2. A list of interactive elements (buttons, inputs, links, etc.) with their approximate locations

Return JSON:
{
    "description": "Detailed description of the screen...",
    "elements": [
        {
            "description": "Element description",
            "type": "button|input|link|text|image|icon|other",
            "x": 100,
            "y": 200,
            "width": 80,
            "height": 30
        }
    ],
    "text_content": ["visible text 1", "visible text 2"]
}

For coordinates, estimate based on a typical 1920x1080 screen. 
Place (0,0) at top-left. Be as accurate as possible."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this screenshot:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
        )
        
        raw_response = response.choices[0].message.content
        
        try:
            data = json.loads(raw_response)
            
            elements = [
                ElementLocation(
                    description=el.get("description", ""),
                    x=el.get("x", 0),
                    y=el.get("y", 0),
                    width=el.get("width"),
                    height=el.get("height"),
                    element_type=el.get("type", "unknown"),
                    confidence=el.get("confidence", 0.8),
                )
                for el in data.get("elements", [])
            ]
            
            return AnalysisResult(
                description=data.get("description", ""),
                elements=elements,
                text_content=data.get("text_content", []),
                raw_response=raw_response,
            )
        except json.JSONDecodeError:
            return AnalysisResult(
                description=raw_response,
                raw_response=raw_response,
            )
    
    def find_element(
        self,
        description: str,
        image_path: Union[str, Path]
    ) -> Optional[ElementLocation]:
        """Find a specific element in the screenshot."""
        image_data = self._encode_image(image_path)
        media_type = self._get_image_media_type(image_path)
        
        system_prompt = f"""You are a UI element locator. Find the element described by the user.

Return JSON:
{{
    "found": true/false,
    "description": "What you found",
    "type": "button|input|link|text|image|icon|other",
    "x": <x coordinate of center>,
    "y": <y coordinate of center>,
    "width": <estimated width>,
    "height": <estimated height>,
    "confidence": <0.0-1.0>
}}

Coordinates should be based on the image dimensions.
If you can't find the element, set found=false and explain in description."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Find this element: {description}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=500,
        )
        
        try:
            data = json.loads(response.choices[0].message.content)
            
            if not data.get("found", False):
                return None
            
            return ElementLocation(
                description=data.get("description", description),
                x=data.get("x", 0),
                y=data.get("y", 0),
                width=data.get("width"),
                height=data.get("height"),
                element_type=data.get("type", "unknown"),
                confidence=data.get("confidence", 0.5),
            )
        except json.JSONDecodeError:
            return None
    
    def plan_action(
        self,
        command: str,
        image_path: Union[str, Path]
    ) -> list[dict]:
        """Plan actions to accomplish a command."""
        image_data = self._encode_image(image_path)
        media_type = self._get_image_media_type(image_path)
        
        system_prompt = """You are a UI automation planner. Given a command and screenshot,
plan the steps needed to accomplish the task.

Return JSON:
{
    "steps": [
        {
            "action": "click|type|scroll|wait",
            "target": "description of element to interact with",
            "value": "text to type or scroll amount (if applicable)",
            "x": <coordinate if known>,
            "y": <coordinate if known>
        }
    ],
    "reasoning": "Brief explanation of the plan"
}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Command: {command}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1000,
        )
        
        try:
            data = json.loads(response.choices[0].message.content)
            return data.get("steps", [])
        except json.JSONDecodeError:
            return []
