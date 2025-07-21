"""
System design and architecture commands
"""

from pathlib import Path
from rich.panel import Panel
from rich.markdown import Markdown

from cli.ai.gemini_client import GeminiClient
from cli.utils.file_manager import FileManager

class DesignCommand:
    """Handle system design and architecture"""
    
    def add_parser(self, subparsers):
        """Add design subcommand parser"""
        parser = subparsers.add_parser('design', help='Generate system architecture and design documents')
        parser.add_argument('action', choices=['architecture', 'database', 'api', 'ui', 'review'], 
                          help='Design action to perform')
        parser.add_argument('--input', '-i', help='Input requirements file')
        parser.add_argument('--output', '-o', help='Output file path')
        parser.add_argument('--type', help='Specific design type or pattern')
        parser.add_argument('--technology', help='Technology stack preference')
        return parser
    
    def execute(self, args, config_manager, console):
        """Execute design command"""
        console.print(f"[bold blue]Design {args.action.title()}[/bold blue]")
        
        gemini_client = GeminiClient(config_manager.get('api_key'))
        file_manager = FileManager()
        
        if args.action == 'architecture':
            self.design_architecture(args, gemini_client, file_manager, console)
        elif args.action == 'database':
            self.design_database(args, gemini_client, file_manager, console)
        elif args.action == 'api':
            self.design_api(args, gemini_client, file_manager, console)
        elif args.action == 'ui':
            self.design_ui(args, gemini_client, file_manager, console)
        elif args.action == 'review':
            self.review_design(args, gemini_client, file_manager, console)
    
    def design_architecture(self, args, gemini_client, file_manager, console):
        """Generate system architecture design"""
        if not args.input:
            console.print("[red]Error: Requirements input file required[/red]")
            return
        
        requirements = file_manager.read_file(args.input)
        technology = args.technology or "modern web technologies"
        console.print("Designing system architecture...")
        
        prompt = f"""
        Design a comprehensive system architecture based on these requirements:
        
        Requirements:
        {requirements}
        
        Technology Stack Preference: {technology}
        
        Please provide:
        1. High-Level Architecture Overview
        2. System Components and their responsibilities
        3. Component Interaction Diagrams (describe in text)
        4. Data Flow Architecture
        5. Technology Stack Recommendations
        6. Deployment Architecture
        7. Scalability Considerations
        8. Security Architecture
        9. Integration Points
        10. Performance Considerations
        11. Monitoring and Logging Strategy
        12. Disaster Recovery Plan
        
        Include ASCII diagrams where possible and detailed explanations.
        Format as clear markdown with proper sections.
        """
        
        try:
            architecture = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(architecture), title="System Architecture Design", border_style="blue")
            console.print(panel)
            
            # Save design
            output_file = args.output or "system_architecture.md"
            file_manager.write_file(output_file, architecture)
            console.print(f"[green]Architecture design saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Architecture design failed: {e}[/red]")
    
    def design_database(self, args, gemini_client, file_manager, console):
        """Generate database design"""
        if not args.input:
            console.print("[red]Error: Requirements input file required[/red]")
            return
        
        requirements = file_manager.read_file(args.input)
        db_type = args.type or "relational"
        console.print("Designing database schema...")
        
        prompt = f"""
        Design a comprehensive database schema based on these requirements:
        
        Requirements:
        {requirements}
        
        Database Type: {db_type}
        
        Please provide:
        1. Database Technology Recommendation
        2. Entity Relationship Diagram (described in text)
        3. Table Schemas with:
           - Table names
           - Column definitions with data types
           - Primary keys
           - Foreign keys
           - Indexes
           - Constraints
        4. Relationships between entities
        5. Database Normalization analysis
        6. Performance optimization strategies
        7. Data migration considerations
        8. Backup and recovery strategy
        9. Security measures (encryption, access control)
        10. Scaling considerations
        
        Provide actual SQL DDL statements for table creation.
        Format as clear markdown with code blocks.
        """
        
        try:
            database_design = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(database_design), title="Database Design", border_style="green")
            console.print(panel)
            
            # Save design
            output_file = args.output or "database_design.md"
            file_manager.write_file(output_file, database_design)
            console.print(f"[green]Database design saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Database design failed: {e}[/red]")
    
    def design_api(self, args, gemini_client, file_manager, console):
        """Generate API design"""
        if not args.input:
            console.print("[red]Error: Requirements input file required[/red]")
            return
        
        requirements = file_manager.read_file(args.input)
        api_type = args.type or "REST"
        console.print("Designing API specification...")
        
        prompt = f"""
        Design a comprehensive API specification based on these requirements:
        
        Requirements:
        {requirements}
        
        API Type: {api_type}
        
        Please provide:
        1. API Architecture Overview
        2. Endpoint Specifications:
           - HTTP methods and URLs
           - Request/Response schemas
           - Status codes
           - Error handling
        3. Authentication and Authorization
        4. Data Models and DTOs
        5. API Versioning Strategy
        6. Rate Limiting and Throttling
        7. Documentation Standards
        8. Testing Strategy
        9. Security Considerations
        10. OpenAPI/Swagger specification
        
        Provide actual endpoint definitions with example requests and responses.
        Include JSON schemas for all data models.
        Format as clear markdown with code blocks.
        """
        
        try:
            api_design = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(api_design), title="API Design", border_style="cyan")
            console.print(panel)
            
            # Save design
            output_file = args.output or "api_design.md"
            file_manager.write_file(output_file, api_design)
            console.print(f"[green]API design saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]API design failed: {e}[/red]")
    
    def design_ui(self, args, gemini_client, file_manager, console):
        """Generate UI/UX design"""
        if not args.input:
            console.print("[red]Error: Requirements input file required[/red]")
            return
        
        requirements = file_manager.read_file(args.input)
        ui_type = args.type or "web"
        console.print("Designing UI/UX...")
        
        prompt = f"""
        Design comprehensive UI/UX specifications based on these requirements:
        
        Requirements:
        {requirements}
        
        UI Type: {ui_type}
        
        Please provide:
        1. User Experience Strategy
        2. User Journey Maps
        3. Information Architecture
        4. Wireframe Descriptions
        5. Component Library Specifications
        6. Design System Guidelines:
           - Color palette
           - Typography
           - Spacing and layout
           - Icons and imagery
        7. Responsive Design Strategy
        8. Accessibility Considerations (WCAG compliance)
        9. Performance Optimization
        10. User Testing Strategy
        11. Prototyping Recommendations
        
        Describe layouts and components in detail.
        Include CSS/styling guidelines.
        Format as clear markdown with detailed descriptions.
        """
        
        try:
            ui_design = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(ui_design), title="UI/UX Design", border_style="magenta")
            console.print(panel)
            
            # Save design
            output_file = args.output or "ui_design.md"
            file_manager.write_file(output_file, ui_design)
            console.print(f"[green]UI design saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]UI design failed: {e}[/red]")
    
    def review_design(self, args, gemini_client, file_manager, console):
        """Review and analyze existing design"""
        if not args.input:
            console.print("[red]Error: Design file required for review[/red]")
            return
        
        design_doc = file_manager.read_file(args.input)
        console.print("Reviewing design...")
        
        prompt = f"""
        Review and analyze the following design document:
        
        Design Document:
        {design_doc}
        
        Please provide:
        1. Design Quality Assessment
        2. Strengths and Best Practices Identified
        3. Potential Issues and Weaknesses
        4. Scalability Analysis
        5. Security Review
        6. Performance Considerations
        7. Maintainability Assessment
        8. Compliance with Best Practices
        9. Recommendations for Improvement
        10. Risk Assessment
        11. Implementation Complexity Analysis
        
        For each category, provide specific feedback and actionable recommendations.
        Rate each aspect on a scale of 1-10 with justification.
        Format as structured markdown with clear sections.
        """
        
        try:
            review = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(review), title="Design Review", border_style="yellow")
            console.print(panel)
            
            # Save review
            output_file = args.output or "design_review.md"
            file_manager.write_file(output_file, review)
            console.print(f"[green]Design review saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Design review failed: {e}[/red]")
    
    def show_detailed_help(self, console):
        """Show detailed help for design command"""
        help_text = """
        # Design Command Help
        
        The design command helps you create comprehensive system designs and architecture using AI.
        
        ## Commands:
        
        ### architecture
        Generate system architecture and component design.
        ```
        ai-engineer design architecture --input requirements.md --technology "Python/React"
        ```
        
        ### database
        Create database schema and design.
        ```
        ai-engineer design database --input requirements.md --type relational
        ```
        
        ### api
        Design API specifications and endpoints.
        ```
        ai-engineer design api --input requirements.md --style RESTful --output api_spec.md
        ```
        
        ### review
        Review existing design for quality and best practices.
        ```
        ai-engineer design review --input architecture.md --output design_review.md
        ```
        """
        
        panel = Panel(Markdown(help_text), title="Design Command Help", border_style="blue")
        console.print(panel)