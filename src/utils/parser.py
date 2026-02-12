"""
Parse and validate production plans
"""

import json
import re
from typing import Dict, Any, Optional


class ProductionPlanParser:
    """Parse and validate production plans from agent output"""
    
    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text that may contain markdown or other content"""
        # Try to find JSON in markdown code blocks
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            json_str = match.group(1)
        else:
            # Try to find raw JSON
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = text[json_start:json_end]
            else:
                return None
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return None
    
    @staticmethod
    def validate_plan(plan: Dict[str, Any]) -> bool:
        """Validate production plan structure"""
        required_fields = ['title', 'total_duration', 'scenes']
        
        for field in required_fields:
            if field not in plan:
                print(f"Missing required field: {field}")
                return False
        
        if not isinstance(plan['scenes'], list) or len(plan['scenes']) == 0:
            print("Scenes must be a non-empty list")
            return False
        
        # Validate each scene
        for i, scene in enumerate(plan['scenes']):
            required_scene_fields = ['scene_number', 'scene_description', 'duration_seconds']
            for field in required_scene_fields:
                if field not in scene:
                    print(f"Scene {i+1} missing field: {field}")
                    return False
        
        return True
