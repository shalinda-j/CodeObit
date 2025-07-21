"""
Debug command for advanced debugging with AI assistance
"""

import ast
import json
import traceback
from pathlib import Path
from datetime import datetime

from cli.commands.base import BaseCommand
from cli.ai.gemini_client import GeminiClient


class DebugCommand(BaseCommand):
    """Advanced debugging with AI assistance"""
    
    def add_parser(self, subparsers):
        parser = subparsers.add_parser('debug', help='Advanced debugging with AI assistance')
        parser.add_argument('file', help='File to debug')
        parser.add_argument('--error', help='Error message or exception to analyze')
        parser.add_argument('--line', type=int, help='Line number where error occurs')
        parser.add_argument('--trace', help='Full stack trace file')
        parser.add_argument('--fix', action='store_true', help='Generate fix suggestions')
        parser.add_argument('--explain', action='store_true', help='Explain the error in detail')
        return parser
    
    def execute(self, args, config_manager, console):
        """Execute debug command"""
        console.print(f"[yellow]🐛 Debugging: {args.file}[/yellow]")
        
        try:
            # Read the file to debug
            file_path = Path(args.file)
            if not file_path.exists():
                console.print(f"[red]✗ File not found: {args.file}[/red]")
                return
            
            with open(file_path, 'r') as f:
                code = f.read()
            
            # Perform static analysis
            issues = self.analyze_code(code, args.file)
            
            # Analyze specific error if provided
            if args.error:
                error_analysis = self.analyze_error(code, args.error, args.line)
                issues.extend(error_analysis)
            
            # Load stack trace if provided
            if args.trace:
                trace_analysis = self.analyze_stack_trace(args.trace, code)
                issues.extend(trace_analysis)
            
            # Display findings
            self.display_debug_results(console, issues, code, args)
            
            # Generate AI-powered fix suggestions
            if args.fix:
                fixes = self.generate_fixes(code, issues, config_manager)
                self.display_fixes(console, fixes)
            
            # Save debug report
            self.save_debug_report(args.file, issues, code)
            
        except Exception as e:
            console.print(f"[red]✗ Debug analysis failed: {e}[/red]")
            traceback.print_exc()
    
    def analyze_code(self, code, filename):
        """Perform static code analysis"""
        issues = []
        
        try:
            # Parse the code to find syntax errors
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'line': e.lineno,
                'message': str(e),
                'severity': 'high'
            })
        
        # Simple pattern-based analysis
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if 'print(' in line and 'debug' in line.lower():
                issues.append({
                    'type': 'debug_statement',
                    'line': i,
                    'message': 'Debug print statement found',
                    'severity': 'low'
                })
            
            if 'TODO' in line or 'FIXME' in line:
                issues.append({
                    'type': 'todo',
                    'line': i,
                    'message': 'TODO or FIXME comment found',
                    'severity': 'medium'
                })
            
            # Check for potential null pointer issues
            if '.get(' not in line and '[' in line and ']' in line:
                if 'dict' in line or 'json' in line:
                    issues.append({
                        'type': 'potential_keyerror',
                        'line': i,
                        'message': 'Potential KeyError - consider using .get() method',
                        'severity': 'medium'
                    })
        
        return issues
    
    def analyze_error(self, code, error_message, line_number=None):
        """Analyze specific error message"""
        issues = []
        
        # Parse common Python errors
        if 'NameError' in error_message:
            issues.append({
                'type': 'name_error',
                'line': line_number,
                'message': 'Variable not defined - check variable names and scope',
                'severity': 'high',
                'error': error_message
            })
        
        elif 'KeyError' in error_message:
            issues.append({
                'type': 'key_error',
                'line': line_number,
                'message': 'Dictionary key not found - use .get() method or check key exists',
                'severity': 'high',
                'error': error_message
            })
        
        elif 'AttributeError' in error_message:
            issues.append({
                'type': 'attribute_error',
                'line': line_number,
                'message': 'Object attribute not found - check object type and available methods',
                'severity': 'high',
                'error': error_message
            })
        
        elif 'ImportError' in error_message or 'ModuleNotFoundError' in error_message:
            issues.append({
                'type': 'import_error',
                'line': line_number,
                'message': 'Module not found - check installation and import path',
                'severity': 'high',
                'error': error_message
            })
        
        return issues
    
    def analyze_stack_trace(self, trace_file, code):
        """Analyze full stack trace"""
        issues = []
        
        try:
            if Path(trace_file).exists():
                with open(trace_file, 'r') as f:
                    trace = f.read()
            else:
                trace = trace_file  # Treat as trace content
            
            # Extract line numbers and error info from trace
            lines = trace.split('\n')
            for line in lines:
                if 'line' in line and ', in' in line:
                    # Extract line number from traceback
                    try:
                        parts = line.split('line ')
                        if len(parts) > 1:
                            line_num = int(parts[1].split(',')[0])
                            issues.append({
                                'type': 'stack_trace',
                                'line': line_num,
                                'message': f'Error occurred in stack trace: {line.strip()}',
                                'severity': 'high'
                            })
                    except (ValueError, IndexError):
                        pass
        
        except Exception as e:
            issues.append({
                'type': 'trace_analysis_error',
                'message': f'Could not analyze stack trace: {e}',
                'severity': 'low'
            })
        
        return issues
    
    def generate_fixes(self, code, issues, config_manager):
        """Generate AI-powered fix suggestions"""
        try:
            client = GeminiClient()
            
            issues_summary = "\n".join([
                f"Line {issue.get('line', 'unknown')}: {issue['message']}"
                for issue in issues
            ])
            
            prompt = f"""
            As a debugging expert, analyze this code and the identified issues.
            Provide specific, actionable fix suggestions:

            CODE:
            ```python
            {code[:2000]}
            ```

            IDENTIFIED ISSUES:
            {issues_summary}

            Please provide:
            1. Root cause analysis
            2. Specific line-by-line fixes
            3. Best practices to prevent similar issues
            4. Code examples of fixes
            """
            
            return client.generate_content(prompt)
        
        except Exception as e:
            return f"AI fix generation failed: {e}"
    
    def display_debug_results(self, console, issues, code, args):
        """Display debug analysis results"""
        from rich.table import Table
        from rich.syntax import Syntax
        
        if not issues:
            console.print("[green]✓ No issues found in code analysis[/green]")
            return
        
        # Create issues table
        table = Table(title="Debug Analysis Results")
        table.add_column("Line", style="cyan", no_wrap=True)
        table.add_column("Type", style="yellow")
        table.add_column("Severity", style="red")
        table.add_column("Message", style="white")
        
        for issue in issues:
            severity_color = {
                'high': '[red]HIGH[/red]',
                'medium': '[yellow]MEDIUM[/yellow]',
                'low': '[green]LOW[/green]'
            }.get(issue.get('severity', 'medium'), '[yellow]MEDIUM[/yellow]')
            
            table.add_row(
                str(issue.get('line', '-')),
                issue.get('type', 'unknown'),
                severity_color,
                issue.get('message', '')
            )
        
        console.print(table)
        
        # Show code snippet around error if line number is available
        if args.line:
            self.show_code_snippet(console, code, args.line)
    
    def show_code_snippet(self, console, code, line_num, context=3):
        """Show code snippet around the error line"""
        from rich.syntax import Syntax
        
        lines = code.split('\n')
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        
        snippet = '\n'.join(lines[start:end])
        syntax = Syntax(snippet, "python", line_numbers=True, start_line=start + 1,
                       highlight_lines=[line_num])
        
        console.print(f"\n[bold blue]Code around line {line_num}:[/bold blue]")
        console.print(syntax)
    
    def display_fixes(self, console, fixes):
        """Display AI-generated fix suggestions"""
        from rich.markdown import Markdown
        
        console.print("\n[bold green]🔧 AI Fix Suggestions:[/bold green]")
        console.print(Markdown(fixes))
    
    def save_debug_report(self, filename, issues, code):
        """Save debug report to file"""
        report = {
            'file': filename,
            'timestamp': datetime.now().isoformat(),
            'issues': issues,
            'code_length': len(code),
            'total_issues': len(issues),
            'high_severity': len([i for i in issues if i.get('severity') == 'high'])
        }
        
        # Save to debug reports directory
        reports_dir = Path("debug_reports")
        reports_dir.mkdir(exist_ok=True)
        
        safe_filename = filename.replace('/', '_').replace('\\', '_')
        report_file = reports_dir / f"debug_{safe_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)