"""
Google Gemini AI client wrapper for the AI Software Engineer CLI
"""

import json
import logging
import os
from typing import Optional, Dict, Any

from google import genai
from google.genai import types
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class GeminiClient:
    """Wrapper for Google Gemini AI client with enhanced functionality for software engineering tasks"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client
        
        Args:
            api_key: Google Gemini API key. If not provided, will use GEMINI_API_KEY environment variable
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        try:
            self.client = genai.Client(api_key=self.api_key)
            self.default_model = "gemini-2.5-flash"
            self.pro_model = "gemini-2.5-pro"
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test the connection to Gemini API
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = self.client.models.generate_content(
                model=self.default_model,
                contents="Hello, test connection"
            )
            return response.text is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def generate_content(self, prompt: str, model: Optional[str] = None, 
                        system_instruction: Optional[str] = None,
                        temperature: float = 0.7) -> str:
        """
        Generate content using Gemini AI
        
        Args:
            prompt: The input prompt
            model: Model to use (defaults to gemini-2.5-flash)
            system_instruction: System instruction for the model
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            str: Generated content
            
        Raises:
            Exception: If content generation fails
        """
        try:
            model_name = model or self.default_model
            
            config = types.GenerateContentConfig(
                temperature=temperature
            )
            
            if system_instruction:
                config.system_instruction = system_instruction
            
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            
            if response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini API")
                return "No content generated"
                
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise Exception(f"Failed to generate content: {e}")
    
    def generate_structured_content(self, prompt: str, response_schema: BaseModel,
                                  model: Optional[str] = None,
                                  system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate structured content with JSON schema validation
        
        Args:
            prompt: The input prompt
            response_schema: Pydantic model for response validation
            model: Model to use (defaults to gemini-2.5-pro for structured output)
            system_instruction: System instruction for the model
            
        Returns:
            Dict[str, Any]: Parsed and validated response
            
        Raises:
            Exception: If structured content generation fails
        """
        try:
            model_name = model or self.pro_model
            
            if not system_instruction:
                system_instruction = (
                    "You are a helpful AI assistant. Respond with valid JSON "
                    "that matches the provided schema exactly."
                )
            
            response = self.client.models.generate_content(
                model=model_name,
                contents=[
                    types.Content(role="user", parts=[types.Part(text=prompt)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
            )
            
            if response.text:
                try:
                    data = json.loads(response.text)
                    # Validate using the schema if it's a Pydantic model
                    try:
                        from pydantic import BaseModel
                        if isinstance(response_schema, type) and issubclass(response_schema, BaseModel):
                            validated_data = response_schema(**data)
                            return validated_data.dict()
                        else:
                            return data
                    except (TypeError, ValueError):
                        return data
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON response: {e}")
                    raise Exception(f"Invalid JSON response: {e}")
                except Exception as e:
                    logger.error(f"Schema validation failed: {e}")
                    raise Exception(f"Response validation failed: {e}")
            else:
                raise Exception("Empty response from Gemini API")
                
        except Exception as e:
            logger.error(f"Structured content generation failed: {e}")
            raise Exception(f"Failed to generate structured content: {e}")
    
    def analyze_code(self, code: str, language: str = "python",
                    analysis_type: str = "comprehensive") -> str:
        """
        Analyze code using Gemini AI
        
        Args:
            code: Code content to analyze
            language: Programming language
            analysis_type: Type of analysis (comprehensive, security, performance, quality)
            
        Returns:
            str: Analysis results
        """
        system_instruction = (
            f"You are an expert software engineer and code reviewer. "
            f"Analyze the provided {language} code for {analysis_type} aspects. "
            f"Provide detailed, actionable feedback with specific recommendations."
        )
        
        prompt = f"""
        Analyze this {language} code:
        
        ```{language}
        {code}
        ```
        
        Analysis focus: {analysis_type}
        
        Please provide a detailed analysis covering relevant aspects such as:
        - Code quality and best practices
        - Performance considerations
        - Security vulnerabilities
        - Maintainability
        - Documentation
        - Error handling
        - Testing recommendations
        
        Format the response as clear, structured markdown.
        """
        
        return self.generate_content(prompt, system_instruction=system_instruction)
    
    def generate_code(self, specification: str, language: str = "python",
                     framework: Optional[str] = None,
                     additional_requirements: Optional[str] = None) -> str:
        """
        Generate code from specifications
        
        Args:
            specification: Code specification or requirements
            language: Target programming language
            framework: Framework to use (optional)
            additional_requirements: Additional requirements or constraints
            
        Returns:
            str: Generated code
        """
        system_instruction = (
            f"You are an expert {language} developer. Generate high-quality, "
            f"production-ready code that follows best practices and conventions. "
            f"Include proper error handling, documentation, and comments."
        )
        
        framework_text = f" using {framework}" if framework else ""
        additional_text = f"\n\nAdditional requirements:\n{additional_requirements}" if additional_requirements else ""
        
        prompt = f"""
        Generate {language} code{framework_text} based on this specification:
        
        {specification}{additional_text}
        
        Requirements:
        - Follow {language} best practices and conventions
        - Include comprehensive error handling
        - Add clear documentation and comments
        - Ensure code is production-ready
        - Include type hints where applicable
        - Follow security best practices
        
        Provide the complete, functional code with explanations.
        """
        
        return self.generate_content(prompt, system_instruction=system_instruction)
    
    def estimate_effort(self, requirements: str, team_size: int = 3,
                       complexity: str = "medium") -> str:
        """
        Estimate development effort for given requirements
        
        Args:
            requirements: Project requirements
            team_size: Size of development team
            complexity: Estimated complexity (low, medium, high)
            
        Returns:
            str: Effort estimation analysis
        """
        system_instruction = (
            "You are an experienced project manager and software architect. "
            "Provide realistic effort estimates based on industry standards "
            "and best practices. Consider all phases of software development."
        )
        
        prompt = f"""
        Estimate development effort for these requirements:
        
        {requirements}
        
        Project parameters:
        - Team size: {team_size} developers
        - Estimated complexity: {complexity}
        
        Provide detailed estimation including:
        - Development phases and timeline
        - Resource requirements
        - Risk factors and mitigation
        - Different scenario estimates (best case, realistic, worst case)
        - Recommendations for project success
        
        Use industry-standard estimation techniques and provide rationale.
        """
        
        return self.generate_content(prompt, system_instruction=system_instruction)
    
    def analyze_image(self, image_path: str, analysis_prompt: Optional[str] = None) -> str:
        """
        Analyze image content using Gemini's multimodal capabilities
        
        Args:
            image_path: Path to the image file
            analysis_prompt: Custom analysis prompt
            
        Returns:
            str: Image analysis results
        """
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
                
            prompt = analysis_prompt or (
                "Analyze this image in detail and describe its key elements, "
                "context, and any notable aspects that might be relevant for "
                "software engineering or project management."
            )
            
            response = self.client.models.generate_content(
                model=self.pro_model,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg",  # Adjust based on actual image type
                    ),
                    prompt,
                ],
            )
            
            return response.text if response.text else "No analysis generated"
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise Exception(f"Failed to analyze image: {e}")
    
    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about available models
        
        Returns:
            Dict[str, str]: Model information
        """
        return {
            "default_model": self.default_model,
            "pro_model": self.pro_model,
            "description": "Gemini AI models for software engineering tasks"
        }
