"""
Advanced Code Review Plugin for CodeObit CLI
Multi-model AI-powered code analysis and review
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from cli.plugins.base import AnalyzerPlugin, PluginMetadata, PluginType

class AdvancedCodeReviewPlugin(AnalyzerPlugin):
    """Advanced code review plugin with multi-AI analysis"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.supported_languages = [
            'python', 'javascript', 'typescript', 'java', 'cpp', 'c',
            'csharp', 'go', 'rust', 'php', 'ruby', 'kotlin', 'swift'
        ]
        self.review_categories = [
            'security', 'performance', 'maintainability', 'bugs',
            'code_style', 'documentation', 'testing', 'architecture'
        ]
    
    def initialize(self, context) -> bool:
        """Initialize the plugin"""
        self.context = context
        self.console = context.console
        self.ai_manager = context.ai_manager
        
        # Register commands
        context.hooks.register('code_review', self.review_code_hook)
        
        return True
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        return True
    
    def get_commands(self) -> Dict[str, callable]:
        """Return plugin commands"""
        return {
            'review': self.review_command,
            'analyze': self.analyze_command,
            'suggest': self.suggest_improvements
        }
    
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code using multiple AI models"""
        if language not in self.supported_languages:
            return {'error': f'Unsupported language: {language}'}
        
        analysis_results = {}
        
        # Get available AI providers
        available_providers = self.ai_manager.list_providers() if hasattr(self.ai_manager, 'list_providers') else []
        
        # Analyze with each available provider
        for provider_info in available_providers:
            if provider_info.get('active', False):
                try:
                    provider_analysis = self._analyze_with_provider(
                        code, language, provider_info['name']
                    )
                    analysis_results[provider_info['name']] = provider_analysis
                except Exception as e:
                    analysis_results[provider_info['name']] = {'error': str(e)}
        
        # Combine and synthesize results
        combined_analysis = self._combine_analyses(analysis_results)
        
        return combined_analysis
    
    def _analyze_with_provider(self, code: str, language: str, provider_name: str) -> Dict[str, Any]:
        """Analyze code with a specific AI provider"""
        
        system_prompt = f"""You are an expert code reviewer. Analyze the following {language} code and provide detailed feedback in the following categories:

1. Security Issues: Identify potential security vulnerabilities
2. Performance: Suggest performance improvements
3. Maintainability: Code structure and readability improvements
4. Bugs: Potential bugs or logical errors
5. Code Style: Adherence to best practices and conventions
6. Documentation: Missing or inadequate documentation
7. Testing: Testability and test coverage suggestions
8. Architecture: Design patterns and architectural improvements

Provide your response in JSON format with the following structure:
{{
  "overall_score": 0-100,
  "categories": {{
    "security": {{"score": 0-100, "issues": [], "suggestions": []}},
    "performance": {{"score": 0-100, "issues": [], "suggestions": []}},
    "maintainability": {{"score": 0-100, "issues": [], "suggestions": []}},
    "bugs": {{"score": 0-100, "issues": [], "suggestions": []}},
    "code_style": {{"score": 0-100, "issues": [], "suggestions": []}},
    "documentation": {{"score": 0-100, "issues": [], "suggestions": []}},
    "testing": {{"score": 0-100, "issues": [], "suggestions": []}},
    "architecture": {{"score": 0-100, "issues": [], "suggestions": []}}
  }},
  "summary": "Overall summary of the code review"
}}"""
        
        try:
            # Get current provider (simplified for demo)
            response = self.ai_manager.generate_content(
                prompt=f"Code to review:\n\n```{language}\n{code}\n```",
                system_instruction=system_prompt
            )
            
            # Try to parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If not JSON, create structured response
                return {
                    'overall_score': 75,
                    'raw_response': response,
                    'provider': provider_name
                }
                
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _combine_analyses(self, analyses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple AI provider analyses into a unified result"""
        
        if not analyses:
            return {'error': 'No analyses available'}
        
        combined = {
            'provider_count': len(analyses),
            'providers': list(analyses.keys()),
            'categories': {},
            'consensus_score': 0,
            'disagreements': [],
            'summary': ''
        }
        
        # Initialize categories
        for category in self.review_categories:
            combined['categories'][category] = {
                'average_score': 0,
                'issues': [],
                'suggestions': [],
                'provider_scores': {}
            }
        
        valid_analyses = [a for a in analyses.values() if 'error' not in a]
        
        if not valid_analyses:
            combined['error'] = 'All analyses failed'
            return combined
        
        # Calculate averages and combine feedback
        for provider, analysis in analyses.items():
            if 'error' in analysis:
                continue
            
            if 'categories' in analysis:
                for category, data in analysis['categories'].items():
                    if category in combined['categories']:
                        combined['categories'][category]['provider_scores'][provider] = data.get('score', 0)
                        combined['categories'][category]['issues'].extend(data.get('issues', []))
                        combined['categories'][category]['suggestions'].extend(data.get('suggestions', []))
        
        # Calculate average scores
        for category in combined['categories']:
            scores = list(combined['categories'][category]['provider_scores'].values())
            if scores:
                combined['categories'][category]['average_score'] = sum(scores) / len(scores)
            
            # Remove duplicates from issues and suggestions
            combined['categories'][category]['issues'] = list(set(combined['categories'][category]['issues']))
            combined['categories'][category]['suggestions'] = list(set(combined['categories'][category]['suggestions']))
        
        # Calculate consensus score
        category_scores = [cat['average_score'] for cat in combined['categories'].values()]
        if category_scores:
            combined['consensus_score'] = sum(category_scores) / len(category_scores)
        
        # Find disagreements (scores differing by more than 20 points)
        for category, data in combined['categories'].items():
            scores = list(data['provider_scores'].values())
            if len(scores) > 1:
                max_score = max(scores)
                min_score = min(scores)
                if max_score - min_score > 20:
                    combined['disagreements'].append({
                        'category': category,
                        'score_range': f"{min_score}-{max_score}",
                        'providers': data['provider_scores']
                    })
        
        # Generate summary
        combined['summary'] = self._generate_summary(combined)
        
        return combined
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a summary of the code review"""
        score = analysis.get('consensus_score', 0)
        
        if score >= 90:
            quality = "Excellent"
        elif score >= 80:
            quality = "Good"
        elif score >= 70:
            quality = "Fair"
        elif score >= 60:
            quality = "Poor"
        else:
            quality = "Very Poor"
        
        summary = f"Code quality: {quality} ({score:.1f}/100)\n"
        
        # Highlight main areas of concern
        categories = analysis.get('categories', {})
        weak_areas = [cat for cat, data in categories.items() if data.get('average_score', 0) < 70]
        
        if weak_areas:
            summary += f"Areas needing improvement: {', '.join(weak_areas)}\n"
        
        if analysis.get('disagreements'):
            summary += f"AI models showed disagreement in {len(analysis['disagreements'])} areas\n"
        
        return summary
    
    def review_command(self, args):
        """Command to review code files"""
        if not hasattr(args, 'file') or not args.file:
            self.console.print("[red]Error: No file specified[/red]")
            return False
        
        file_path = Path(args.file)
        if not file_path.exists():
            self.console.print(f"[red]Error: File not found: {file_path}[/red]")
            return False
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Detect language from file extension
            language = self._detect_language(file_path)
            
            self.console.print(f"[cyan]Reviewing {file_path} ({language})...[/cyan]")
            
            # Analyze code
            analysis = self.analyze_code(code, language)
            
            # Display results
            self._display_analysis(analysis, file_path)
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error reviewing file: {e}[/red]")
            return False
    
    def analyze_command(self, args):
        """Command to analyze project structure"""
        project_info = self.context.project_manager.get_current_project_info()
        
        if not project_info.get('is_loaded'):
            self.console.print("[yellow]No active project. Analyzing current directory...[/yellow]")
            project_path = Path.cwd()
        else:
            project_path = Path(project_info['data']['path'])
        
        # Find code files
        code_files = self._find_code_files(project_path)
        
        if not code_files:
            self.console.print("[yellow]No code files found to analyze[/yellow]")
            return False
        
        self.console.print(f"[cyan]Analyzing {len(code_files)} files...[/cyan]")
        
        # Analyze each file
        results = {}
        for file_path in code_files[:5]:  # Limit to first 5 files for demo
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                language = self._detect_language(file_path)
                analysis = self.analyze_code(code, language)
                results[str(file_path)] = analysis
                
            except Exception as e:
                results[str(file_path)] = {'error': str(e)}
        
        # Display project-level analysis
        self._display_project_analysis(results)
        
        return True
    
    def suggest_improvements(self, args):
        """Command to suggest specific improvements"""
        # Implementation for improvement suggestions
        self.console.print("[cyan]Improvement suggestions feature coming soon![/cyan]")
        return True
    
    def review_code_hook(self, code: str, language: str):
        """Hook for programmatic code review"""
        return self.analyze_code(code, language)
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.kt': 'kotlin',
            '.swift': 'swift'
        }
        
        return extension_map.get(file_path.suffix.lower(), 'text')
    
    def _find_code_files(self, directory: Path) -> List[Path]:
        """Find code files in directory"""
        code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php', '.rb', '.kt', '.swift']
        code_files = []
        
        for ext in code_extensions:
            code_files.extend(directory.rglob(f'*{ext}'))
        
        return code_files
    
    def _display_analysis(self, analysis: Dict[str, Any], file_path: Path):
        """Display code analysis results"""
        if 'error' in analysis:
            self.console.print(f"[red]Analysis failed: {analysis['error']}[/red]")
            return
        
        # Create results panel
        score = analysis.get('consensus_score', 0)
        summary = analysis.get('summary', 'No summary available')
        
        panel = Panel(
            f"[bold]{file_path.name}[/bold]\n\n"
            f"[green]Overall Score: {score:.1f}/100[/green]\n\n"
            f"{summary}",
            title="Code Review Results",
            border_style="cyan"
        )
        
        self.console.print(panel)
        
        # Category details table
        if 'categories' in analysis:
            table = Table(title="Category Breakdown")
            table.add_column("Category", style="cyan")
            table.add_column("Score", style="yellow")
            table.add_column("Issues", style="red")
            table.add_column("Suggestions", style="green")
            
            for category, data in analysis['categories'].items():
                issues_count = len(data.get('issues', []))
                suggestions_count = len(data.get('suggestions', []))
                score = data.get('average_score', 0)
                
                table.add_row(
                    category.replace('_', ' ').title(),
                    f"{score:.1f}",
                    str(issues_count),
                    str(suggestions_count)
                )
            
            self.console.print(table)
    
    def _display_project_analysis(self, results: Dict[str, Dict[str, Any]]):
        """Display project-level analysis results"""
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if not valid_results:
            self.console.print("[red]No valid analysis results[/red]")
            return
        
        # Calculate project averages
        total_score = sum(r.get('consensus_score', 0) for r in valid_results.values())
        avg_score = total_score / len(valid_results) if valid_results else 0
        
        # File results table
        table = Table(title="Project Analysis Results")
        table.add_column("File", style="cyan")
        table.add_column("Score", style="yellow")
        table.add_column("Status", style="green")
        
        for file_path, result in results.items():
            file_name = Path(file_path).name
            if 'error' in result:
                table.add_row(file_name, "N/A", f"Error: {result['error']}")
            else:
                score = result.get('consensus_score', 0)
                status = "Good" if score >= 80 else "Needs Review" if score >= 60 else "Poor"
                table.add_row(file_name, f"{score:.1f}", status)
        
        self.console.print(table)
        
        # Project summary
        summary_panel = Panel(
            f"[bold]Project Code Quality Summary[/bold]\n\n"
            f"[green]Average Score: {avg_score:.1f}/100[/green]\n"
            f"Files Analyzed: {len(valid_results)}\n"
            f"Files with Errors: {len(results) - len(valid_results)}",
            title="Project Overview",
            border_style="green"
        )
        
        self.console.print(summary_panel)
    
    def get_supported_languages(self) -> List[str]:
        """Return supported languages"""
        return self.supported_languages