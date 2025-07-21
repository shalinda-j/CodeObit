"""
Code generation and analysis commands
"""

import os
from pathlib import Path
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax

from cli.ai.gemini_client import GeminiClient
from cli.utils.file_manager import FileManager

class CodeCommand:
    """Handle code generation and analysis"""
    
    def add_parser(self, subparsers):
        """Add code subcommand parser"""
        parser = subparsers.add_parser('code', help='AI-powered code generation and analysis')
        parser.add_argument('action', choices=['generate', 'analyze', 'optimize', 'refactor', 'complete', 'explain'], 
                          help='Code action to perform')
        parser.add_argument('--input', '-i', help='Input file or specification')
        parser.add_argument('--output', '-o', help='Output file path')
        parser.add_argument('--language', '-l', help='Programming language')
        parser.add_argument('--framework', help='Framework to use')
        parser.add_argument('--pattern', help='Design pattern to apply')
        parser.add_argument('--function', help='Specific function or method name')
        return parser
    
    def execute(self, args, config_manager, console):
        """Execute code command"""
        console.print(f"[bold blue]Code {args.action.title()}[/bold blue]")
        
        gemini_client = GeminiClient(config_manager.get('api_key'))
        file_manager = FileManager()
        
        if args.action == 'generate':
            self.generate_code(args, gemini_client, file_manager, console)
        elif args.action == 'analyze':
            self.analyze_code(args, gemini_client, file_manager, console)
        elif args.action == 'optimize':
            self.optimize_code(args, gemini_client, file_manager, console)
        elif args.action == 'refactor':
            self.refactor_code(args, gemini_client, file_manager, console)
        elif args.action == 'complete':
            self.complete_code(args, gemini_client, file_manager, console)
        elif args.action == 'explain':
            self.explain_code(args, gemini_client, file_manager, console)
    
    def generate_code(self, args, gemini_client, file_manager, console):
        """Generate code from specifications"""
        if not args.input:
            console.print("[red]Error: Input specification required[/red]")
            return
        
        # Read specification
        if Path(args.input).exists():
            specification = file_manager.read_file(args.input)
        else:
            specification = args.input
        
        language = args.language or "Python"
        framework = args.framework or ""
        pattern = args.pattern or ""
        
        console.print(f"Generating {language} code...")
        
        prompt = f"""
        Generate high-quality, production-ready code based on this specification:
        
        Specification:
        {specification}
        
        Requirements:
        - Programming Language: {language}
        - Framework: {framework if framework else "Use best practices for the language"}
        - Design Pattern: {pattern if pattern else "Apply appropriate patterns"}
        
        Please provide:
        1. Complete, functional code implementation
        2. Proper error handling and validation
        3. Comprehensive comments and documentation
        4. Unit tests (if applicable)
        5. Configuration files if needed
        6. Installation/setup instructions
        7. Usage examples
        8. Performance considerations
        9. Security best practices implementation
        10. Code structure explanation
        
        Ensure the code follows language-specific best practices and conventions.
        Include proper imports, dependencies, and project structure.
        """
        
        try:
            generated_code = gemini_client.generate_content(prompt)
            
            # Display code with syntax highlighting
            try:
                # Try to extract code blocks for syntax highlighting
                lines = generated_code.split('\n')
                in_code_block = False
                current_code = []
                current_language = language.lower()
                
                for line in lines:
                    if line.strip().startswith('```'):
                        if in_code_block:
                            # End of code block
                            if current_code:
                                code_text = '\n'.join(current_code)
                                syntax = Syntax(code_text, current_language, theme="monokai", line_numbers=True)
                                console.print(syntax)
                                current_code = []
                            in_code_block = False
                        else:
                            # Start of code block
                            if line.strip().startswith('```') and len(line.strip()) > 3:
                                current_language = line.strip()[3:] or language.lower()
                            in_code_block = True
                    elif in_code_block:
                        current_code.append(line)
                    else:
                        console.print(line)
                
            except Exception:
                # Fallback to regular display
                panel = Panel(Markdown(generated_code), title="Generated Code", border_style="green")
                console.print(panel)
            
            # Save code
            output_file = args.output or f"generated_code.{self.get_file_extension(language)}"
            file_manager.write_file(output_file, generated_code)
            console.print(f"[green]Code saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Code generation failed: {e}[/red]")
    
    def analyze_code(self, args, gemini_client, file_manager, console):
        """Analyze existing code"""
        if not args.input:
            console.print("[red]Error: Code file required for analysis[/red]")
            return
        
        code_content = file_manager.read_file(args.input)
        language = args.language or self.detect_language(args.input)
        console.print(f"Analyzing {language} code...")
        
        prompt = f"""
        Perform a comprehensive analysis of this {language} code:
        
        Code:
        {code_content}
        
        Please provide:
        1. Code Quality Assessment (1-10 rating)
        2. Code Structure and Organization
        3. Best Practices Compliance
        4. Performance Analysis
        5. Security Vulnerabilities
        6. Maintainability Assessment
        7. Code Complexity Analysis
        8. Documentation Quality
        9. Error Handling Review
        10. Testing Coverage Assessment
        11. Specific Issues Found
        12. Improvement Recommendations
        
        For each issue, provide:
        - Severity level (High, Medium, Low)
        - Line numbers if applicable
        - Specific recommendations for fixes
        
        Format as structured markdown with clear sections.
        """
        
        try:
            analysis = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(analysis), title="Code Analysis Report", border_style="yellow")
            console.print(panel)
            
            # Save analysis
            output_file = args.output or "code_analysis.md"
            file_manager.write_file(output_file, analysis)
            console.print(f"[green]Analysis saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Code analysis failed: {e}[/red]")
    
    def optimize_code(self, args, gemini_client, file_manager, console):
        """Optimize existing code for performance"""
        if not args.input:
            console.print("[red]Error: Code file required for optimization[/red]")
            return
        
        code_content = file_manager.read_file(args.input)
        language = args.language or self.detect_language(args.input)
        console.print(f"Optimizing {language} code...")
        
        prompt = f"""
        Optimize this {language} code for better performance and efficiency:
        
        Original Code:
        {code_content}
        
        Please provide:
        1. Optimized version of the code
        2. Performance improvements made
        3. Memory usage optimizations
        4. Algorithm improvements
        5. Data structure optimizations
        6. Caching strategies applied
        7. Database query optimizations (if applicable)
        8. Concurrency improvements
        9. I/O operation optimizations
        10. Before/after performance comparison
        11. Benchmarking recommendations
        12. Monitoring suggestions
        
        Ensure the optimized code maintains the same functionality.
        Explain each optimization with comments.
        Include performance metrics where possible.
        """
        
        try:
            optimization = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(optimization), title="Code Optimization", border_style="green")
            console.print(panel)
            
            # Save optimized code
            output_file = args.output or f"optimized_{Path(args.input).name}"
            file_manager.write_file(output_file, optimization)
            console.print(f"[green]Optimized code saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Code optimization failed: {e}[/red]")
    
    def refactor_code(self, args, gemini_client, file_manager, console):
        """Refactor code for better structure and maintainability"""
        if not args.input:
            console.print("[red]Error: Code file required for refactoring[/red]")
            return
        
        code_content = file_manager.read_file(args.input)
        language = args.language or self.detect_language(args.input)
        pattern = args.pattern or ""
        console.print(f"Refactoring {language} code...")
        
        prompt = f"""
        Refactor this {language} code to improve structure and maintainability:
        
        Original Code:
        {code_content}
        
        Apply these principles:
        - SOLID principles
        - DRY (Don't Repeat Yourself)
        - Clean Code practices
        - Design pattern: {pattern if pattern else "Choose appropriate patterns"}
        
        Please provide:
        1. Refactored code with improved structure
        2. Explanation of changes made
        3. Design patterns applied
        4. Code organization improvements
        5. Function/method extraction
        6. Class structure improvements
        7. Dependency injection (if applicable)
        8. Error handling improvements
        9. Code readability enhancements
        10. Testing improvements
        11. Migration guide from old to new structure
        
        Ensure all functionality is preserved.
        Add comprehensive comments explaining the refactoring.
        """
        
        try:
            refactoring = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(refactoring), title="Code Refactoring", border_style="blue")
            console.print(panel)
            
            # Save refactored code
            output_file = args.output or f"refactored_{Path(args.input).name}"
            file_manager.write_file(output_file, refactoring)
            console.print(f"[green]Refactored code saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Code refactoring failed: {e}[/red]")
    
    def complete_code(self, args, gemini_client, file_manager, console):
        """Complete partial code implementation"""
        if not args.input:
            console.print("[red]Error: Partial code file required[/red]")
            return
        
        partial_code = file_manager.read_file(args.input)
        language = args.language or self.detect_language(args.input)
        function_name = args.function or ""
        console.print(f"Completing {language} code...")
        
        prompt = f"""
        Complete this partial {language} code implementation:
        
        Partial Code:
        {partial_code}
        
        Focus on completing: {function_name if function_name else "all incomplete parts"}
        
        Please provide:
        1. Complete, functional implementation
        2. Missing function implementations
        3. Proper error handling
        4. Input validation
        5. Edge case handling
        6. Documentation and comments
        7. Type hints (if language supports)
        8. Unit tests for new functions
        9. Integration considerations
        10. Performance considerations
        
        Maintain consistency with existing code style and patterns.
        Ensure all TODOs and incomplete sections are addressed.
        """
        
        try:
            completion = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(completion), title="Code Completion", border_style="cyan")
            console.print(panel)
            
            # Save completed code
            output_file = args.output or f"completed_{Path(args.input).name}"
            file_manager.write_file(output_file, completion)
            console.print(f"[green]Completed code saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Code completion failed: {e}[/red]")
    
    def explain_code(self, args, gemini_client, file_manager, console):
        """Explain how code works"""
        if not args.input:
            console.print("[red]Error: Code file required for explanation[/red]")
            return
        
        code_content = file_manager.read_file(args.input)
        language = args.language or self.detect_language(args.input)
        console.print(f"Explaining {language} code...")
        
        prompt = f"""
        Provide a comprehensive explanation of this {language} code:
        
        Code:
        {code_content}
        
        Please explain:
        1. Overall purpose and functionality
        2. Code structure and organization
        3. Key algorithms and logic
        4. Data structures used
        5. Function/method breakdown
        6. Control flow explanation
        7. Dependencies and imports
        8. Design patterns used
        9. Performance characteristics
        10. Potential issues or edge cases
        11. How to use/integrate this code
        12. Maintenance considerations
        
        Format as clear markdown with:
        - High-level overview
        - Detailed section-by-section explanation
        - Code flow diagrams (text-based)
        - Examples of usage
        - Technical concepts explained in simple terms
        """
        
        try:
            explanation = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(explanation), title="Code Explanation", border_style="magenta")
            console.print(panel)
            
            # Save explanation
            output_file = args.output or "code_explanation.md"
            file_manager.write_file(output_file, explanation)
            console.print(f"[green]Explanation saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Code explanation failed: {e}[/red]")
    
    def detect_language(self, file_path):
        """Detect programming language from file extension"""
        extension = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.sql': 'SQL'
        }
        return language_map.get(extension, 'Unknown')
    
    def get_file_extension(self, language):
        """Get file extension for programming language"""
        extension_map = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java',
            'c++': 'cpp',
            'c': 'c',
            'c#': 'cs',
            'php': 'php',
            'ruby': 'rb',
            'go': 'go',
            'rust': 'rs',
            'swift': 'swift',
            'kotlin': 'kt',
            'scala': 'scala',
            'html': 'html',
            'css': 'css',
            'sql': 'sql'
        }
        return extension_map.get(language.lower(), 'txt')
    
    def show_detailed_help(self, console):
        """Show detailed help for code command"""
        help_text = """
        # Code Command Help
        
        The code command provides AI-powered code generation, analysis, and optimization capabilities.
        
        ## Commands:
        
        ### generate
        Generate code from specifications or requirements.
        ```
        ai-engineer code generate --input "Create a REST API for user management" --language Python --framework Flask
        ```
        
        ### analyze
        Analyze existing code for quality, security, and performance.
        ```
        ai-engineer code analyze --input app.py --output analysis.md
        ```
        
        ### optimize
        Optimize code for performance and best practices.
        ```
        ai-engineer code optimize --input app.py --output optimized_app.py
        ```
        
        ### convert
        Convert code between programming languages.
        ```
        ai-engineer code convert --input app.py --from Python --to JavaScript
        ```
        """
        
        panel = Panel(Markdown(help_text), title="Code Command Help", border_style="blue")
        console.print(panel)