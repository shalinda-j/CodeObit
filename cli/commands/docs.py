"""
Documentation generation and management commands
"""

from pathlib import Path
from rich.panel import Panel
from rich.markdown import Markdown

from cli.ai.gemini_client import GeminiClient
from cli.utils.file_manager import FileManager

class DocsCommand:
    """Handle documentation generation and management"""
    
    def add_parser(self, subparsers):
        """Add docs subcommand parser"""
        parser = subparsers.add_parser('docs', help='Automated documentation generation')
        parser.add_argument('action', choices=['generate', 'api', 'user', 'technical', 'update'], 
                          help='Documentation action to perform')
        parser.add_argument('--input', '-i', help='Input code file or project directory')
        parser.add_argument('--output', '-o', help='Output documentation file path')
        parser.add_argument('--format', choices=['markdown', 'html', 'pdf', 'rst'], 
                          default='markdown', help='Output format')
        parser.add_argument('--template', help='Documentation template to use')
        parser.add_argument('--audience', help='Target audience (developer, user, admin)')
        return parser
    
    def execute(self, args, config_manager, console):
        """Execute docs command"""
        console.print(f"[bold blue]Documentation {args.action.title()}[/bold blue]")
        
        gemini_client = GeminiClient(config_manager.get('api_key'))
        file_manager = FileManager()
        
        if args.action == 'generate':
            self.generate_docs(args, gemini_client, file_manager, console)
        elif args.action == 'api':
            self.generate_api_docs(args, gemini_client, file_manager, console)
        elif args.action == 'user':
            self.generate_user_docs(args, gemini_client, file_manager, console)
        elif args.action == 'technical':
            self.generate_technical_docs(args, gemini_client, file_manager, console)
        elif args.action == 'update':
            self.update_docs(args, gemini_client, file_manager, console)
    
    def generate_docs(self, args, gemini_client, file_manager, console):
        """Generate comprehensive documentation"""
        if not args.input:
            console.print("[red]Error: Input code file or project directory required[/red]")
            return
        
        # Read input content
        if Path(args.input).is_file():
            content = file_manager.read_file(args.input)
        else:
            console.print("[yellow]Directory processing not fully implemented, analyzing as single file[/yellow]")
            content = file_manager.read_file(args.input)
        
        audience = args.audience or "developer"
        doc_format = args.format
        console.print(f"Generating {audience} documentation in {doc_format} format...")
        
        prompt = f"""
        Generate comprehensive documentation for this code/project:
        
        Content:
        {content}
        
        Target Audience: {audience}
        Output Format: {doc_format}
        
        Create documentation that includes:
        
        1. Overview Section:
           - Project description and purpose
           - Key features and capabilities
           - Architecture overview
           - Technology stack
        
        2. Getting Started:
           - Prerequisites and requirements
           - Installation instructions
           - Quick start guide
           - Basic usage examples
        
        3. Detailed Documentation:
           - API reference (if applicable)
           - Function/method documentation
           - Configuration options
           - Usage patterns and examples
        
        4. Code Documentation:
           - Class and function descriptions
           - Parameter explanations
           - Return value documentation
           - Exception handling
        
        5. Examples and Tutorials:
           - Code examples
           - Use case scenarios
           - Best practices
           - Common patterns
        
        6. Configuration:
           - Configuration files
           - Environment variables
           - Settings explanation
           - Customization options
        
        7. Troubleshooting:
           - Common issues and solutions
           - Error messages explanation
           - Debugging guidance
           - FAQ section
        
        8. Advanced Topics:
           - Performance considerations
           - Security guidelines
           - Scalability aspects
           - Integration patterns
        
        9. Reference:
           - Complete API reference
           - Command-line options
           - Configuration reference
           - Glossary of terms
        
        10. Appendices:
            - Change log
            - Migration guides
            - License information
            - Contributing guidelines
        
        Format the documentation appropriately for {doc_format}.
        Include proper headings, code blocks, tables, and cross-references.
        Make it comprehensive yet easy to navigate.
        """
        
        try:
            documentation = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(documentation), title="Generated Documentation", border_style="green")
            console.print(panel)
            
            # Save documentation
            output_file = args.output or f"documentation.{doc_format}"
            file_manager.write_file(output_file, documentation)
            console.print(f"[green]Documentation saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Documentation generation failed: {e}[/red]")
    
    def generate_api_docs(self, args, gemini_client, file_manager, console):
        """Generate API documentation"""
        if not args.input:
            console.print("[red]Error: API code or specification file required[/red]")
            return
        
        api_content = file_manager.read_file(args.input)
        doc_format = args.format
        console.print(f"Generating API documentation in {doc_format} format...")
        
        prompt = f"""
        Generate comprehensive API documentation for this code:
        
        API Code/Specification:
        {api_content}
        
        Output Format: {doc_format}
        
        Create API documentation that includes:
        
        1. API Overview:
           - API description and purpose
           - Base URL and versioning
           - Authentication methods
           - Rate limiting information
        
        2. Authentication:
           - Authentication methods (API keys, OAuth, JWT)
           - Authorization scopes
           - Security considerations
           - Example authentication flows
        
        3. Endpoints Documentation:
           For each endpoint, provide:
           - HTTP method and URL
           - Description and purpose
           - Request parameters (path, query, body)
           - Request headers
           - Request body schema
           - Response codes and meanings
           - Response body schema
           - Example requests and responses
        
        4. Data Models:
           - Request/response schemas
           - Data types and formats
           - Validation rules
           - Example data structures
        
        5. Error Handling:
           - Error response format
           - Common error codes
           - Error message explanations
           - Troubleshooting guide
        
        6. SDK and Code Examples:
           - Code examples in multiple languages
           - SDK usage examples
           - Integration patterns
           - Best practices
        
        7. Rate Limiting:
           - Rate limit policies
           - Headers and responses
           - Handling rate limits
           - Best practices
        
        8. Webhooks (if applicable):
           - Webhook setup
           - Event types
           - Payload formats
           - Security considerations
        
        9. Testing:
           - Testing strategies
           - Mock responses
           - Testing tools
           - Sandbox environment
        
        10. Migration and Versioning:
            - API versioning strategy
            - Migration guides
            - Deprecation policies
            - Backward compatibility
        
        Format as OpenAPI/Swagger specification where possible.
        Include interactive examples and clear navigation.
        """
        
        try:
            api_docs = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(api_docs), title="API Documentation", border_style="blue")
            console.print(panel)
            
            # Save API documentation
            output_file = args.output or f"api_documentation.{doc_format}"
            file_manager.write_file(output_file, api_docs)
            console.print(f"[green]API documentation saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]API documentation generation failed: {e}[/red]")
    
    def generate_user_docs(self, args, gemini_client, file_manager, console):
        """Generate user-facing documentation"""
        if not args.input:
            console.print("[red]Error: Application or feature specification required[/red]")
            return
        
        app_content = file_manager.read_file(args.input)
        doc_format = args.format
        console.print(f"Generating user documentation in {doc_format} format...")
        
        prompt = f"""
        Generate user-facing documentation for this application:
        
        Application/Feature Description:
        {app_content}
        
        Output Format: {doc_format}
        
        Create user documentation that includes:
        
        1. Introduction:
           - What the application does
           - Key benefits and features
           - Who should use it
           - System requirements
        
        2. Getting Started:
           - Account setup process
           - First-time user guide
           - Initial configuration
           - Quick start tutorial
        
        3. User Interface Guide:
           - Navigation overview
           - Screen descriptions
           - Menu explanations
           - Button and control descriptions
        
        4. Feature Documentation:
           For each feature:
           - Feature overview
           - Step-by-step instructions
           - Screenshots/illustrations (describe)
           - Tips and best practices
           - Common use cases
        
        5. Tutorials and Workflows:
           - Common task walkthroughs
           - End-to-end workflows
           - Advanced usage scenarios
           - Integration with other tools
        
        6. Settings and Configuration:
           - User preferences
           - Account settings
           - Privacy controls
           - Notification settings
        
        7. Troubleshooting:
           - Common issues and solutions
           - Error message explanations
           - Performance tips
           - When to contact support
        
        8. FAQ:
           - Frequently asked questions
           - Common misconceptions
           - Feature limitations
           - Billing/pricing questions
        
        9. Tips and Best Practices:
           - Efficiency tips
           - Security recommendations
           - Optimization suggestions
           - Advanced techniques
        
        10. Support and Resources:
            - Contact information
            - Community resources
            - Training materials
            - Additional resources
        
        Write in clear, non-technical language.
        Use step-by-step instructions with numbered lists.
        Include warnings and important notes where needed.
        Make it scannable with good headings and formatting.
        """
        
        try:
            user_docs = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(user_docs), title="User Documentation", border_style="cyan")
            console.print(panel)
            
            # Save user documentation
            output_file = args.output or f"user_guide.{doc_format}"
            file_manager.write_file(output_file, user_docs)
            console.print(f"[green]User documentation saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]User documentation generation failed: {e}[/red]")
    
    def generate_technical_docs(self, args, gemini_client, file_manager, console):
        """Generate technical documentation"""
        if not args.input:
            console.print("[red]Error: Technical specification or code required[/red]")
            return
        
        tech_content = file_manager.read_file(args.input)
        doc_format = args.format
        console.print(f"Generating technical documentation in {doc_format} format...")
        
        prompt = f"""
        Generate comprehensive technical documentation:
        
        Technical Content:
        {tech_content}
        
        Output Format: {doc_format}
        
        Create technical documentation that includes:
        
        1. System Architecture:
           - High-level architecture diagram (describe)
           - Component interactions
           - Technology stack
           - Design patterns used
           - Scalability considerations
        
        2. Database Design:
           - Entity relationship diagrams
           - Schema documentation
           - Indexing strategy
           - Migration procedures
           - Performance considerations
        
        3. API Technical Specification:
           - Internal API documentation
           - Service interfaces
           - Message formats
           - Protocol specifications
           - Error handling strategies
        
        4. Code Architecture:
           - Module organization
           - Class hierarchies
           - Design patterns implementation
           - Code organization principles
           - Dependency management
        
        5. Infrastructure:
           - Deployment architecture
           - Environment configurations
           - CI/CD pipeline documentation
           - Monitoring and logging
           - Disaster recovery procedures
        
        6. Security Architecture:
           - Security model
           - Authentication/authorization flows
           - Data protection measures
           - Security controls
           - Threat mitigation strategies
        
        7. Performance and Scalability:
           - Performance requirements
           - Bottleneck analysis
           - Scaling strategies
           - Optimization techniques
           - Monitoring approaches
        
        8. Integration Specifications:
           - External system integrations
           - Protocol specifications
           - Data exchange formats
           - Error handling procedures
           - Retry mechanisms
        
        9. Development Guidelines:
           - Coding standards
           - Development workflow
           - Testing strategies
           - Code review process
           - Release procedures
        
        10. Operations Manual:
            - Deployment procedures
            - Configuration management
            - Monitoring and alerting
            - Troubleshooting procedures
            - Maintenance tasks
        
        11. Technical Decision Records:
            - Architecture decisions
            - Technology choices
            - Trade-off analysis
            - Future considerations
        
        Include detailed technical diagrams (described in text).
        Provide code examples and configuration samples.
        Make it comprehensive for technical audiences.
        """
        
        try:
            tech_docs = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(tech_docs), title="Technical Documentation", border_style="magenta")
            console.print(panel)
            
            # Save technical documentation
            output_file = args.output or f"technical_documentation.{doc_format}"
            file_manager.write_file(output_file, tech_docs)
            console.print(f"[green]Technical documentation saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Technical documentation generation failed: {e}[/red]")
    
    def update_docs(self, args, gemini_client, file_manager, console):
        """Update existing documentation"""
        if not args.input:
            console.print("[red]Error: Existing documentation file required[/red]")
            return
        
        existing_docs = file_manager.read_file(args.input)
        console.print("Updating existing documentation...")
        
        prompt = f"""
        Update and improve this existing documentation:
        
        Current Documentation:
        {existing_docs}
        
        Please:
        1. Review for accuracy and completeness
        2. Update outdated information
        3. Improve clarity and readability
        4. Add missing sections or details
        5. Fix formatting and structure issues
        6. Enhance examples and explanations
        7. Add table of contents if missing
        8. Improve cross-references and links
        9. Update code examples and snippets
        10. Ensure consistency in style and tone
        
        Specific improvements to make:
        - Better organization and structure
        - More comprehensive examples
        - Clearer explanations of complex concepts
        - Updated best practices
        - Enhanced troubleshooting sections
        - Improved navigation aids
        - Better formatting and readability
        - More detailed API documentation
        - Enhanced user guidance
        - Updated references and links
        
        Provide the updated documentation with:
        - Summary of changes made
        - Explanation of improvements
        - Recommendations for future updates
        - Quality assessment of the updated version
        
        Maintain the original intent while significantly improving quality and usability.
        """
        
        try:
            updated_docs = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(updated_docs), title="Updated Documentation", border_style="yellow")
            console.print(panel)
            
            # Save updated documentation
            output_file = args.output or f"updated_{Path(args.input).name}"
            file_manager.write_file(output_file, updated_docs)
            console.print(f"[green]Updated documentation saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Documentation update failed: {e}[/red]")
    
    def show_detailed_help(self, console):
        """Show detailed help for docs command"""
        help_text = """
        # Documentation Command Help
        
        The docs command provides automated documentation generation for various audiences and formats.
        
        ## Commands:
        
        ### generate
        Generate comprehensive documentation from code.
        ```
        ai-engineer docs generate --input app.py --audience developer --format markdown
        ```
        
        ### api
        Generate API documentation.
        ```
        ai-engineer docs api --input api_spec.py --format html --output api_docs.html
        ```
        
        ### user
        Generate user-facing documentation.
        ```
        ai-engineer docs user --input features.md --format markdown --output user_guide.md
        ```
        
        ### technical
        Generate technical documentation.
        ```
        ai-engineer docs technical --input architecture.md --format rst --output tech_docs.rst
        ```
        
        ### update
        Update and improve existing documentation.
        ```
        ai-engineer docs update --input old_docs.md --output improved_docs.md
        ```
        
        ## Options:
        - `--input, -i`: Input code file or project directory
        - `--output, -o`: Output documentation file path
        - `--format`: Output format (markdown, html, pdf, rst)
        - `--template`: Documentation template to use
        - `--audience`: Target audience (developer, user, admin)
        """
        
        panel = Panel(Markdown(help_text), title="Documentation Command Help", border_style="blue")
        console.print(panel)
