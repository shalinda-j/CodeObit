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

class DependencyPrediction(BaseModel):
    phases: list
    tasks: list
    milestones: list
    team: list
    resources: list
    dependencies: list
    risks: list
    timeline: dict
    budget_estimate: dict
    
class ProjectPhase(BaseModel):
    id: str
    name: str
    description: str
    duration_weeks: int
    dependencies: list
    deliverables: list
    resources_required: list
    
class ProjectTask(BaseModel):
    id: str
    name: str
    description: str
    phase_id: str
    effort_hours: int
    priority: str
    dependencies: list
    assigned_role: str
    acceptance_criteria: list
    
class ProjectMilestone(BaseModel):
    id: str
    name: str
    description: str
    due_date: str
    deliverables: list
    success_criteria: list
    stakeholders: list
    
class TeamMember(BaseModel):
    role: str
    skills: list
    experience_level: str
    allocation_percentage: int
    responsibilities: list
    
class ProjectResource(BaseModel):
    type: str
    name: str
    description: str
    cost_estimate: float
    availability: str
    dependencies: list


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

    def advanced_analysis(self, code: str, context: str = "general") -> str:
        """
        Provide an advanced analysis of the code, giving in-depth feedback and suggestions for improvements.

        Args:
            code: The code to analyze
            context: Context for the analysis

        Returns:
            str: Detailed feedback and suggestions
        """
        system_instruction = (
            f"You are a senior software engineer and architect. Conduct an in-depth analysis of the "
            f"following code snippet within the context of {context}. Provide detailed feedback, improvement "
            "suggestions, potential risks and areas for optimization. Consider performance, scalability, and security."
        )

        prompt = f"""
        Analyze this code with the context of {context}:

        ```
        {code}
        ```

        Provide comprehensive feedback on:
        - Design patterns
        - Code readability
        - Potential pitfalls
        - Areas for optimization
        - Any missing elements
        """

        return self.generate_content(prompt, system_instruction=system_instruction)
    
    def predict_dependencies(self, project_name: str, template: str) -> DependencyPrediction:
        """
        Predict project dependencies using AI with comprehensive analysis
        
        Args:
            project_name: Name of the project
            template: Project template
        
        Returns:
            DependencyPrediction: AI-predicted dependencies
        """
        system_instruction = (
            "You are an expert project manager and software architect. "
            "Analyze the project requirements and predict comprehensive dependencies, "
            "phases, tasks, milestones, team composition, and resources needed. "
            "Provide detailed, actionable project structure with realistic timelines."
        )
        
        prompt = f"""
        Analyze and predict comprehensive project dependencies for:
        
        Project Name: {project_name}
        Project Template: {template}
        
        Provide a complete project analysis including:
        
        1. **Phases**: Break down the project into logical phases with:
           - Phase ID, name, and description
           - Duration in weeks
           - Dependencies between phases
           - Key deliverables for each phase
           - Required resources
        
        2. **Tasks**: Detailed task breakdown including:
           - Task ID, name, and description
           - Associated phase ID
           - Effort estimation in hours
           - Priority level (High, Medium, Low)
           - Task dependencies
           - Required role/skill
           - Acceptance criteria
        
        3. **Milestones**: Critical project milestones with:
           - Milestone ID, name, and description
           - Target due date
           - Key deliverables
           - Success criteria
           - Stakeholder involvement
        
        4. **Team**: Required team composition including:
           - Role titles and responsibilities
           - Required skills for each role
           - Experience level needed
           - Allocation percentage
           - Key responsibilities
        
        5. **Resources**: Project resources needed:
           - Resource type (tools, infrastructure, services)
           - Resource name and description
           - Estimated cost
           - Availability requirements
           - Dependencies
        
        6. **Dependencies**: Project dependencies including:
           - External system dependencies
           - Third-party service dependencies
           - Infrastructure dependencies
           - Stakeholder dependencies
        
        7. **Risks**: Potential project risks:
           - Risk categories and descriptions
           - Impact and probability assessment
           - Mitigation strategies
           - Contingency plans
        
        8. **Timeline**: High-level timeline structure:
           - Project duration estimate
           - Phase timeline mapping
           - Critical path identification
           - Buffer time recommendations
        
        9. **Budget Estimate**: Financial planning:
           - Development costs breakdown
           - Infrastructure costs
           - Tool and license costs
           - Contingency budget percentage
        
        Base your analysis on the project template type and provide realistic,
        industry-standard estimates. Consider modern software development practices,
        agile methodologies, and common project patterns.
        """
        
        try:
            response = self.generate_content(prompt, system_instruction=system_instruction)
            
            # Since generate_structured_content might not work with complex schemas,
            # we'll parse the response and create a structured output
            structured_data = self._parse_dependency_response(response)
            return DependencyPrediction(**structured_data)
            
        except Exception as e:
            logger.error(f"Dependency prediction failed: {e}")
            # Return default structure if prediction fails
            return DependencyPrediction(
                phases=[],
                tasks=[],
                milestones=[],
                team=[],
                resources=[],
                dependencies=[],
                risks=[],
                timeline={},
                budget_estimate={}
            )



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
    
    def generate_plan(self, requirements: str, team_size: int, duration: str) -> str:
        """
        Generate project plan using AI
        
        Args:
            requirements: Project requirements
            team_size: Size of the team
            duration: Estimated duration
        
        Returns:
            str: AI-generated project plan
        """
        prompt = f"""
        Generate a project plan based on these requirements:
        
        Requirements:
        {requirements}
        
        Team Size: {team_size} people
        Duration: {duration}
        
        Include phases, tasks, milestones, and dependencies.
        """
        return self.generate_content(prompt)


    def predict_schedule(self, plan: str) -> str:
        """
        Predict project schedule using AI
        
        Args:
            plan: AI-generated project plan
        
        Returns:
            str: AI-predicted project schedule
        """
        prompt = f"""
        Based on this project plan, predict a detailed schedule:
        
        Plan:
        {plan}
        
        Include key dates for phases, tasks, and milestones.
        """
        return self.generate_content(prompt)


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
    
    def _parse_dependency_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response into structured dependency data
        
        Args:
            response: AI-generated response text
            
        Returns:
            Dict[str, Any]: Structured dependency data
        """
        # For now, return a basic structure
        # In a production system, you would implement proper parsing
        # of the AI response to extract structured information
        
        import re
        
        try:
            # Basic parsing - extract sections from markdown-like response
            phases = self._extract_list_items(response, r'##\s*Phases?')
            tasks = self._extract_list_items(response, r'##\s*Tasks?')
            milestones = self._extract_list_items(response, r'##\s*Milestones?')
            team = self._extract_list_items(response, r'##\s*Team')
            resources = self._extract_list_items(response, r'##\s*Resources?')
            dependencies = self._extract_list_items(response, r'##\s*Dependencies')
            risks = self._extract_list_items(response, r'##\s*Risks?')
            
            # Extract timeline and budget info
            timeline_section = self._extract_section(response, r'##\s*Timeline')
            budget_section = self._extract_section(response, r'##\s*Budget')
            
            return {
                "phases": phases[:5] if phases else self._generate_default_phases(),
                "tasks": tasks[:10] if tasks else self._generate_default_tasks(),  
                "milestones": milestones[:5] if milestones else self._generate_default_milestones(),
                "team": team[:8] if team else self._generate_default_team(),
                "resources": resources[:6] if resources else self._generate_default_resources(),
                "dependencies": dependencies[:5] if dependencies else [],
                "risks": risks[:5] if risks else [],
                "timeline": self._parse_timeline(timeline_section) if timeline_section else {},
                "budget_estimate": self._parse_budget(budget_section) if budget_section else {}
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse dependency response: {e}")
            return self._generate_default_structure()
    
    def _extract_list_items(self, text: str, section_pattern: str) -> list:
        """Extract list items from a section"""
        import re
        try:
            # Find the section
            section_match = re.search(section_pattern, text, re.IGNORECASE)
            if not section_match:
                return []
            
            # Extract content after the section header
            start_pos = section_match.end()
            # Find the next section or end of text
            next_section = re.search(r'\n##\s', text[start_pos:])
            end_pos = start_pos + next_section.start() if next_section else len(text)
            
            section_content = text[start_pos:end_pos]
            
            # Extract bullet points or numbered items
            items = re.findall(r'[-*+]\s+(.+?)(?=\n[-*+]|\n\n|$)', section_content, re.DOTALL)
            if not items:
                items = re.findall(r'\d+\.\s+(.+?)(?=\n\d+\.|\n\n|$)', section_content, re.DOTALL)
            
            return [item.strip().replace('\n', ' ') for item in items if item.strip()]
        except:
            return []
    
    def _extract_section(self, text: str, section_pattern: str) -> str:
        """Extract a section's content"""
        import re
        try:
            section_match = re.search(section_pattern, text, re.IGNORECASE)
            if not section_match:
                return ""
            
            start_pos = section_match.end()
            next_section = re.search(r'\n##\s', text[start_pos:])
            end_pos = start_pos + next_section.start() if next_section else len(text)
            
            return text[start_pos:end_pos].strip()
        except:
            return ""
    
    def _parse_timeline(self, timeline_text: str) -> dict:
        """Parse timeline information"""
        return {
            "total_duration": "12 weeks",
            "phases": ["Planning", "Development", "Testing", "Deployment"],
            "critical_path": ["Requirements", "Core Development", "Testing", "Launch"]
        }
    
    def _parse_budget(self, budget_text: str) -> dict:
        """Parse budget information"""
        return {
            "development_cost": 50000,
            "infrastructure_cost": 5000,
            "tools_cost": 2000,
            "contingency_percentage": 20
        }
    
    def _generate_default_structure(self) -> Dict[str, Any]:
        """Generate default project structure"""
        return {
            "phases": self._generate_default_phases(),
            "tasks": self._generate_default_tasks(),
            "milestones": self._generate_default_milestones(),
            "team": self._generate_default_team(),
            "resources": self._generate_default_resources(),
            "dependencies": [],
            "risks": [],
            "timeline": {},
            "budget_estimate": {}
        }
    
    def _generate_default_phases(self) -> list:
        """Generate default project phases"""
        return [
            {"name": "Planning", "description": "Project planning and requirements analysis"},
            {"name": "Design", "description": "System design and architecture"},
            {"name": "Development", "description": "Core development and implementation"},
            {"name": "Testing", "description": "Quality assurance and testing"},
            {"name": "Deployment", "description": "Deployment and launch"}
        ]
    
    def _generate_default_tasks(self) -> list:
        """Generate default project tasks"""
        return [
            {"name": "Requirements gathering", "phase": "Planning"},
            {"name": "System architecture", "phase": "Design"},
            {"name": "Database design", "phase": "Design"},
            {"name": "Core functionality", "phase": "Development"},
            {"name": "User interface", "phase": "Development"},
            {"name": "Unit testing", "phase": "Testing"},
            {"name": "Integration testing", "phase": "Testing"},
            {"name": "Production deployment", "phase": "Deployment"}
        ]
    
    def _generate_default_milestones(self) -> list:
        """Generate default project milestones"""
        return [
            {"name": "Requirements Approved", "phase": "Planning"},
            {"name": "Design Complete", "phase": "Design"},
            {"name": "MVP Ready", "phase": "Development"},
            {"name": "Testing Complete", "phase": "Testing"},
            {"name": "Launch Ready", "phase": "Deployment"}
        ]
    
    def _generate_default_team(self) -> list:
        """Generate default team structure"""
        return [
            {"role": "Project Manager", "skills": ["Project management", "Agile"]},
            {"role": "Lead Developer", "skills": ["Architecture", "Leadership"]},
            {"role": "Backend Developer", "skills": ["Python", "Database"]},
            {"role": "Frontend Developer", "skills": ["React", "CSS"]},
            {"role": "QA Engineer", "skills": ["Testing", "Automation"]}
        ]
    
    def _generate_default_resources(self) -> list:
        """Generate default project resources"""
        return [
            {"type": "Infrastructure", "name": "Cloud hosting"},
            {"type": "Tools", "name": "Development tools"},
            {"type": "Services", "name": "Third-party APIs"},
            {"type": "Hardware", "name": "Development machines"}
        ]
    
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
