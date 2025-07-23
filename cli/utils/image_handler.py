"""
Image upload and processing system for CodeObit CLI
Supports image analysis using AI vision capabilities
"""

import os
import base64
import mimetypes
from pathlib import Path
from typing import Optional, Dict, List, Union
from PIL import Image
import io
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class ImageHandler:
    """Handle image uploads and processing for the CLI"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        self.max_size_mb = 10  # Maximum file size in MB
        self.image_cache: Dict[str, Dict] = {}
        
    def process_image(self, image_path: str, analysis_prompt: Optional[str] = None) -> Dict:
        """
        Process an uploaded image
        
        Args:
            image_path: Path to the image file
            analysis_prompt: Optional prompt for AI analysis
            
        Returns:
            Dictionary with image info and analysis
        """
        try:
            path = Path(image_path)
            
            # Validate image file
            validation_result = self._validate_image(path)
            if not validation_result['valid']:
                return validation_result
            
            # Get image metadata
            image_info = self._get_image_info(path)
            
            # Resize if necessary
            processed_path = self._resize_if_needed(path)
            
            # Convert to base64 for AI analysis
            base64_data = self._image_to_base64(processed_path)
            
            result = {
                'valid': True,
                'path': str(path),
                'processed_path': str(processed_path),
                'info': image_info,
                'base64_data': base64_data,
                'ready_for_ai': True
            }
            
            # Cache the result
            self.image_cache[str(path)] = result
            
            return result
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Error processing image: {str(e)}",
                'path': image_path
            }
    
    def _validate_image(self, path: Path) -> Dict:
        """Validate image file"""
        if not path.exists():
            return {'valid': False, 'error': f"Image file not found: {path}"}
        
        if not path.is_file():
            return {'valid': False, 'error': f"Path is not a file: {path}"}
        
        # Check file extension
        if path.suffix.lower() not in self.supported_formats:
            return {
                'valid': False, 
                'error': f"Unsupported format: {path.suffix}. Supported: {', '.join(self.supported_formats)}"
            }
        
        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.max_size_mb:
            return {
                'valid': False, 
                'error': f"Image too large: {size_mb:.1f}MB. Maximum: {self.max_size_mb}MB"
            }
        
        # Try to open with PIL to verify it's a valid image
        try:
            with Image.open(path) as img:
                img.verify()
            return {'valid': True}
        except Exception as e:
            return {'valid': False, 'error': f"Invalid image file: {str(e)}"}
    
    def _get_image_info(self, path: Path) -> Dict:
        """Get detailed image information"""
        try:
            with Image.open(path) as img:
                info = {
                    'filename': path.name,
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,  # (width, height)
                    'width': img.size[0],
                    'height': img.size[1],
                    'file_size': path.stat().st_size,
                    'mime_type': mimetypes.guess_type(str(path))[0],
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
                
                # Get additional metadata if available
                if hasattr(img, '_getexif') and img._getexif():
                    info['has_exif'] = True
                else:
                    info['has_exif'] = False
                
                return info
                
        except Exception as e:
            return {'error': f"Could not read image info: {str(e)}"}
    
    def _resize_if_needed(self, path: Path, max_dimension: int = 1024) -> Path:
        """Resize image if it's too large for AI processing"""
        try:
            with Image.open(path) as img:
                width, height = img.size
                
                # If image is small enough, return original path
                if max(width, height) <= max_dimension:
                    return path
                
                # Calculate new dimensions
                if width > height:
                    new_width = max_dimension
                    new_height = int((height * max_dimension) / width)
                else:
                    new_height = max_dimension
                    new_width = int((width * max_dimension) / height)
                
                # Resize image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save resized image
                resized_path = path.parent / f"resized_{path.name}"
                resized_img.save(resized_path, optimize=True, quality=85)
                
                return resized_path
                
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not resize image: {e}[/yellow]")
            return path
    
    def _image_to_base64(self, path: Path) -> str:
        """Convert image to base64 string for AI analysis"""
        try:
            with open(path, "rb") as image_file:
                base64_data = base64.b64encode(image_file.read()).decode('utf-8')
                return base64_data
        except Exception as e:
            raise Exception(f"Could not encode image to base64: {e}")
    
    def show_image_info(self, image_path: str) -> None:
        """Display image information in a nice table"""
        result = self.process_image(image_path)
        
        if not result['valid']:
            self.console.print(f"[red]❌ {result['error']}[/red]")
            return
        
        info = result['info']
        
        # Create info table
        table = Table(title=f"📸 Image Information: {info['filename']}")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Format", info.get('format', 'Unknown'))
        table.add_row("Dimensions", f"{info.get('width', 0)} × {info.get('height', 0)} pixels")
        table.add_row("File Size", f"{info.get('file_size', 0) / 1024:.1f} KB")
        table.add_row("Color Mode", info.get('mode', 'Unknown'))
        table.add_row("MIME Type", info.get('mime_type', 'Unknown'))
        table.add_row("Has Transparency", "Yes" if info.get('has_transparency', False) else "No")
        table.add_row("Has EXIF", "Yes" if info.get('has_exif', False) else "No")
        table.add_row("AI Ready", "✅ Yes" if result.get('ready_for_ai', False) else "❌ No")
        
        self.console.print(table)
    
    def analyze_image_with_ai(self, image_path: str, analysis_prompt: str, provider_manager) -> Optional[str]:
        """
        Analyze image using AI vision capabilities
        
        Args:
            image_path: Path to image file
            analysis_prompt: Prompt for AI analysis
            provider_manager: AI provider manager instance
            
        Returns:
            AI analysis result or None if failed
        """
        try:
            # Process the image
            result = self.process_image(image_path)
            
            if not result['valid']:
                self.console.print(f"[red]Cannot analyze image: {result['error']}[/red]")
                return None
            
            # Check if current provider supports image analysis
            provider = provider_manager.get_current_provider()
            if not provider:
                self.console.print("[red]No active AI provider available[/red]")
                return None
            
            # For now, we'll use a text-based analysis since we need to implement vision API
            # This is a placeholder that would need actual vision API integration
            
            info = result['info']
            description = f\"\"\"Image Analysis Request:\n\nImage Details:\n- Filename: {info['filename']}\n- Format: {info.get('format', 'Unknown')}\n- Dimensions: {info.get('width', 0)} × {info.get('height', 0)} pixels\n- File Size: {info.get('file_size', 0) / 1024:.1f} KB\n- Color Mode: {info.get('mode', 'Unknown')}\n\nUser Request: {analysis_prompt}\n\nNote: This is a placeholder for image analysis. To enable full image analysis, implement vision API integration with the current AI provider.\"\"\"\n            \n            # Generate analysis using text prompt (placeholder)\n            analysis = provider.generate_content(\n                f\"Based on this image information, provide analysis for: {analysis_prompt}\\n\\n{description}\",\n                system_instruction=\"You are an AI assistant helping with image analysis. Provide helpful analysis based on the image metadata provided.\"\n            )\n            \n            return analysis\n            \n        except Exception as e:\n            self.console.print(f\"[red]Error analyzing image: {e}[/red]\")\n            return None
    
    def save_image_to_project(self, image_path: str, project_data: Dict) -> bool:\n        \"\"\"Save image information to project data\"\"\"\n        try:\n            result = self.process_image(image_path)\n            \n            if not result['valid']:\n                return False\n            \n            # Initialize images array if not exists\n            if 'images' not in project_data:\n                project_data['images'] = []\n            \n            # Create image record\n            image_record = {\n                'path': result['path'],\n                'info': result['info'],\n                'uploaded_at': os.path.getctime(result['path']),\n                'processed': result['ready_for_ai']\n            }\n            \n            # Check if image already exists\n            existing_idx = next(\n                (i for i, img in enumerate(project_data['images']) \n                 if img['path'] == result['path']), \n                None\n            )\n            \n            if existing_idx is not None:\n                project_data['images'][existing_idx] = image_record\n            else:\n                project_data['images'].append(image_record)\n            \n            return True\n            \n        except Exception as e:\n            self.console.print(f\"[red]Error saving image to project: {e}[/red]\")\n            return False
    \n    def list_supported_formats(self) -> None:\n        \"\"\"Display supported image formats\"\"\"\n        formats_table = Table(title=\"📸 Supported Image Formats\")\n        formats_table.add_column(\"Extension\", style=\"cyan\")\n        formats_table.add_column(\"Description\", style=\"white\")\n        \n        format_descriptions = {\n            '.jpg': 'JPEG - Compressed image format',\n            '.jpeg': 'JPEG - Compressed image format',\n            '.png': 'PNG - Lossless compression with transparency',\n            '.gif': 'GIF - Animated images and simple graphics',\n            '.bmp': 'BMP - Uncompressed bitmap format',\n            '.webp': 'WebP - Modern image format by Google',\n            '.tiff': 'TIFF - High-quality image format'\n        }\n        \n        for ext in sorted(self.supported_formats):\n            description = format_descriptions.get(ext, 'Supported image format')\n            formats_table.add_row(ext.upper(), description)\n        \n        self.console.print(formats_table)\n        self.console.print(f\"\\n[cyan]Maximum file size:[/cyan] {self.max_size_mb} MB\")\n        self.console.print(f\"[cyan]Maximum dimension for AI:[/cyan] 1024 pixels\")\n\n# Global instance\n_image_handler: Optional[ImageHandler] = None\n\ndef get_image_handler() -> ImageHandler:\n    \"\"\"Get or create global image handler\"\"\"\n    global _image_handler\n    if _image_handler is None:\n        _image_handler = ImageHandler()\n    return _image_handler
