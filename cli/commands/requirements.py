"""
Requirements analysis and management commands
"""

import json
from pathlib import Path
from rich.panel import Panel
from rich.markdown import Markdown

from cli.ai.gemini_client import GeminiClient
from cli.utils.file_manager import FileManager

class RequirementsCommand:
    """Handle requirements analysis and management"""
    
    def add_parser(self, subparsers):
        """Add requirements subcommand parser"""
        parser = subparsers.add_parser('requirements', help='Analyze and manage project requirements')
        parser.add_argument('action', choices=['analyze', 'generate', 'validate', 'refine'], 
                          help='Requirements action to perform')
        parser.add_argument('--input', '-i', help='Input file or text')
        parser.add_argument('--output', '-o', help='Output file path')
        parser.add_argument('--format', choices=['json', 'markdown', 'yaml'], 
                          default='markdown', help='Output format')
        parser.add_argument('--stakeholder', help='Stakeholder perspective (user, developer, business)')
        return parser
    
    def execute(self, args, config_manager, console):
        """Execute requirements command"""
        console.print(f"[bold blue]Requirements {args.action.title()}[/bold blue]")
        
        gemini_client = GeminiClient(config_manager.get('api_key'))
        file_manager = FileManager()
        
        if args.action == 'analyze':
            self.analyze_requirements(args, gemini_client, file_manager, console)
        elif args.action == 'generate':
            self.generate_requirements(args, gemini_client, file_manager, console)
        elif args.action == 'validate':
            self.validate_requirements(args, gemini_client, file_manager, console)
        elif args.action == 'refine':
            self.refine_requirements(args, gemini_client, file_manager, console)
    
    def analyze_requirements(self, args, gemini_client, file_manager, console):
        """Analyze existing requirements"""
        if not args.input:
            console.print("[red]Error: Input file or text required for analysis[/red]")
            return
        
        # Read input
        if Path(args.input).exists():
            requirements_text = file_manager.read_file(args.input)
        else:
            requirements_text = args.input
        
        console.print("Analyzing requirements...")
        
        prompt = f"""
        Analyze the following requirements and provide a comprehensive analysis:
        
        Requirements:
        {requirements_text}
        
        Please provide:
        1. Functional Requirements (numbered list)
        2. Non-functional Requirements (performance, security, usability, etc.)
        3. Technical Requirements (technology stack, infrastructure, etc.)
        4. Business Requirements (objectives, constraints, success criteria)
        5. User Stories (if applicable)
        6. Potential Issues or Ambiguities
        7. Recommendations for improvement
        
        Format the response in clear markdown with proper sections.
        """
        
        try:
            analysis = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(analysis), title="Requirements Analysis", border_style="green")
            console.print(panel)
            
            # Save to output file if specified
            if args.output:
                file_manager.write_file(args.output, analysis)
                console.print(f"[green]Analysis saved to: {args.output}[/green]")
                
        except Exception as e:
            console.print(f"[red]Analysis failed: {e}[/red]")
    
    def generate_requirements(self, args, gemini_client, file_manager, console):
        """Generate requirements from project description"""
        if not args.input:
            console.print("[red]Error: Project description required[/red]")
            return
        
        # Read project description
        if Path(args.input).exists():
            project_desc = file_manager.read_file(args.input)
        else:
            project_desc = args.input
        
        stakeholder = args.stakeholder or "user"
        console.print(f"Generating requirements from {stakeholder} perspective...")
        
        prompt = f"""
        Generate comprehensive software requirements based on this project description:
        
        Project Description:
        {project_desc}
        
        Generate requirements from the perspective of: {stakeholder}
        
        Please create:
        1. Executive Summary
        2. Functional Requirements (with unique IDs like FR-001)
        3. Non-functional Requirements (with unique IDs like NFR-001)
        4. Technical Requirements
        5. User Stories (As a [user], I want [goal] so that [benefit])
        6. Acceptance Criteria for each requirement
        7. Priority levels (High, Medium, Low)
        8. Dependencies between requirements
        9. Success Metrics
        
        Format as clear markdown with proper sections and tables where appropriate.
        """
        
        try:
            requirements = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(requirements), title="Generated Requirements", border_style="blue")
            console.print(panel)
            
            # Save to output file
            output_file = args.output or f"requirements_{stakeholder}.md"
            file_manager.write_file(output_file, requirements)
            console.print(f"[green]Requirements saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Requirements generation failed: {e}[/red]")
    
    def validate_requirements(self, args, gemini_client, file_manager, console):
        """Validate requirements for completeness and quality"""
        if not args.input:
            console.print("[red]Error: Requirements file required for validation[/red]")
            return
        
        requirements_text = file_manager.read_file(args.input)
        console.print("Validating requirements...")
        
        prompt = f"""
        Validate the following requirements document for quality and completeness:
        
        Requirements:
        {requirements_text}
        
        Check for:
        1. Completeness - Are all necessary requirements covered?
        2. Clarity - Are requirements clearly stated and unambiguous?
        3. Consistency - Are there any conflicting requirements?
        4. Feasibility - Are requirements technically feasible?
        5. Testability - Can requirements be tested and verified?
        6. Traceability - Are requirements properly organized and numbered?
        7. Priority - Are priorities clearly defined?
        8. Scope - Is the scope well-defined and bounded?
        
        For each category, provide:
        - Score (1-10)
        - Issues found
        - Specific recommendations for improvement
        
        Format as structured markdown with clear sections.
        """
        
        try:
            validation = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(validation), title="Requirements Validation", border_style="yellow")
            console.print(panel)
            
            # Save validation report
            output_file = args.output or "requirements_validation.md"
            file_manager.write_file(output_file, validation)
            console.print(f"[green]Validation report saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Validation failed: {e}[/red]")
    
    def refine_requirements(self, args, gemini_client, file_manager, console):
        """Refine and improve existing requirements"""
        if not args.input:
            console.print("[red]Error: Requirements file required for refinement[/red]")
            return
        
        requirements_text = file_manager.read_file(args.input)
        console.print("Refining requirements...")
        
        prompt = f"""
        Refine and improve the following requirements document:
        
        Current Requirements:
        {requirements_text}
        
        Please:
        1. Improve clarity and remove ambiguity
        2. Add missing details and specifications
        3. Ensure proper structure and organization
        4. Add acceptance criteria where missing
        5. Improve traceability with proper IDs
        6. Add priority levels if missing
        7. Resolve any inconsistencies
        8. Enhance testability
        9. Add risk considerations
        10. Improve formatting and readability
        
        Provide the refined requirements document in clear markdown format.
        Include a summary of changes made at the beginning.
        """
        
        try:
            refined_requirements = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(refined_requirements), title="Refined Requirements", border_style="green")
            console.print(panel)
            
            # Save refined requirements
            output_file = args.output or "requirements_refined.md"
            file_manager.write_file(output_file, refined_requirements)
            console.print(f"[green]Refined requirements saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Requirements refinement failed: {e}[/red]")
    
    def show_detailed_help(self, console):
        """Show detailed help for requirements command"""
        help_text = """
        # Requirements Command Help
        
        The requirements command helps you analyze, generate, validate, and refine software requirements using AI.
        
        ## Commands:
        
        ### analyze
        Analyze existing requirements for structure and completeness.
        ```
        ai-engineer requirements analyze --input requirements.txt --output analysis.md
        ```
        
        ### generate
        Generate comprehensive requirements from a project description.
        ```
        ai-engineer requirements generate --description "E-commerce platform" --output requirements.md
        ```
        
        ### validate
        Validate requirements for completeness and consistency.
        ```
        ai-engineer requirements validate --input requirements.md --output validation_report.md
        ```
        
        ### refine
        Refine and improve existing requirements.
        ```
        ai-engineer requirements refine --input requirements.md --output refined_requirements.md
        ```
        """
        
        panel = Panel(Markdown(help_text), title="Requirements Command Help", border_style="blue")
        console.print(panel)