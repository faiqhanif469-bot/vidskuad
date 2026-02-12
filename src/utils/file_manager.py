"""
File management utilities
"""

import json
from pathlib import Path
from typing import Any, Dict


class FileManager:
    """Manage file operations"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
    
    def save_json(self, data: Dict[str, Any], filename: str, subdir: str = "output"):
        """Save data as JSON"""
        output_dir = self.base_dir / subdir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def load_json(self, filename: str, subdir: str = "output") -> Dict[str, Any]:
        """Load JSON file"""
        filepath = self.base_dir / subdir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_text(self, text: str, filename: str, subdir: str = "output"):
        """Save text file"""
        output_dir = self.base_dir / subdir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return str(filepath)
    
    def load_text(self, filename: str, subdir: str = "scripts") -> str:
        """Load text file"""
        filepath = self.base_dir / subdir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
