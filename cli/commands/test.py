"""
Testing and test case generation commands
"""

from pathlib import Path
from rich.panel import Panel
from rich.markdown import Markdown

from cli.ai.gemini_client import GeminiClient
from cli.utils.file_manager import FileManager

class TestCommand:
    """Handle testing and test case generation"""
    
    def add_parser(self, subparsers):
        """Add test subcommand parser"""
        parser = subparsers.add_parser('test', help='Automated testing and test case generation')
        parser.add_argument('action', choices=['generate', 'analyze', 'strategy', 'coverage', 'performance'], 
                          help='Test action to perform')
        parser.add_argument('--input', '-i', help='Input code file or test specification')
        parser.add_argument('--output', '-o', help='Output test file path')
        parser.add_argument('--framework', help='Testing framework to use')
        parser.add_argument('--type', help='Type of tests (unit, integration, e2e)')
        parser.add_argument('--coverage', help='Target coverage percentage', type=int, default=80)
        return parser
    
    def execute(self, args, config_manager, console):
        """Execute test command"""
        console.print(f"[bold blue]Test {args.action.title()}[/bold blue]")
        
        gemini_client = GeminiClient(config_manager.get('api_key'))
        file_manager = FileManager()
        
        if args.action == 'generate':
            self.generate_tests(args, gemini_client, file_manager, console)
        elif args.action == 'analyze':
            self.analyze_tests(args, gemini_client, file_manager, console)
        elif args.action == 'strategy':
            self.create_test_strategy(args, gemini_client, file_manager, console)
        elif args.action == 'coverage':
            self.analyze_coverage(args, gemini_client, file_manager, console)
        elif args.action == 'performance':
            self.generate_performance_tests(args, gemini_client, file_manager, console)
    
    def generate_tests(self, args, gemini_client, file_manager, console):
        """Generate comprehensive test suites"""
        if not args.input:
            console.print("[red]Error: Input code file required[/red]")
            return
        
        code_content = file_manager.read_file(args.input)
        framework = args.framework or "pytest"
        test_type = args.type or "unit"
        coverage_target = args.coverage
        
        console.print(f"Generating {test_type} tests using {framework}...")
        
        prompt = f"""
        Generate comprehensive {test_type} tests for this code using {framework}:
        
        Code to test:
        {code_content}
        
        Target coverage: {coverage_target}%
        
        Please generate:
        1. Complete test suite with proper structure
        2. Test cases covering:
           - Normal operation scenarios
           - Edge cases and boundary conditions
           - Error conditions and exception handling
           - Input validation tests
           - Mocking external dependencies
        3. Setup and teardown methods
        4. Test data fixtures
        5. Parameterized tests where appropriate
        6. Integration tests (if applicable)
        7. Mock configurations
        8. Test utilities and helpers
        9. Performance benchmarks
        10. Documentation for running tests
        
        Follow these testing best practices:
        - Clear, descriptive test names
        - Arrange-Act-Assert pattern
        - Independent test cases
        - Proper assertions
        - Error message validation
        - Test isolation
        
        Include setup instructions and dependencies.
        Format with proper code blocks and explanations.
        """
        
        try:
            test_code = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(test_code), title="Generated Test Suite", border_style="green")
            console.print(panel)
            
            # Save test code
            output_file = args.output or f"test_{Path(args.input).stem}.py"
            file_manager.write_file(output_file, test_code)
            console.print(f"[green]Test suite saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Test generation failed: {e}[/red]")
    
    def analyze_tests(self, args, gemini_client, file_manager, console):
        """Analyze existing test suite"""
        if not args.input:
            console.print("[red]Error: Test file required for analysis[/red]")
            return
        
        test_content = file_manager.read_file(args.input)
        console.print("Analyzing test suite...")
        
        prompt = f"""
        Analyze this test suite for quality and completeness:
        
        Test Code:
        {test_content}
        
        Please evaluate:
        1. Test Coverage Analysis
           - Functions/methods covered
           - Code paths tested
           - Edge cases covered
           - Missing test scenarios
        
        2. Test Quality Assessment
           - Test structure and organization
           - Assertion quality
           - Test independence
           - Error handling tests
           - Performance test coverage
        
        3. Best Practices Compliance
           - Naming conventions
           - Test documentation
           - Setup/teardown usage
           - Mocking strategies
           - Test data management
        
        4. Maintainability
           - Code duplication
           - Test readability
           - Refactoring opportunities
           - Documentation quality
        
        5. Performance
           - Test execution speed
           - Resource usage
           - Optimization opportunities
        
        6. Specific Issues Found
           - Flaky tests potential
           - Brittle assertions
           - Missing validations
           - Security test gaps
        
        7. Improvement Recommendations
           - Additional test cases needed
           - Framework usage improvements
           - Structural improvements
        
        Provide specific line references and actionable recommendations.
        Rate each category on a scale of 1-10 with justification.
        """
        
        try:
            analysis = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(analysis), title="Test Suite Analysis", border_style="yellow")
            console.print(panel)
            
            # Save analysis
            output_file = args.output or "test_analysis.md"
            file_manager.write_file(output_file, analysis)
            console.print(f"[green]Test analysis saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Test analysis failed: {e}[/red]")
    
    def create_test_strategy(self, args, gemini_client, file_manager, console):
        """Create comprehensive testing strategy"""
        if not args.input:
            console.print("[red]Error: Project requirements or code base required[/red]")
            return
        
        project_info = file_manager.read_file(args.input)
        console.print("Creating testing strategy...")
        
        prompt = f"""
        Create a comprehensive testing strategy for this project:
        
        Project Information:
        {project_info}
        
        Please provide:
        1. Testing Pyramid Strategy
           - Unit testing approach
           - Integration testing plan
           - End-to-end testing strategy
           - API testing methodology
        
        2. Test Framework Selection
           - Recommended testing frameworks
           - Tool justifications
           - Setup and configuration
        
        3. Test Environment Strategy
           - Development testing
           - Staging environment tests
           - Production monitoring
           - CI/CD integration
        
        4. Test Data Management
           - Test data strategy
           - Data generation approaches
           - Database testing
           - Privacy considerations
        
        5. Performance Testing
           - Load testing strategy
           - Stress testing approach
           - Performance benchmarks
           - Monitoring and alerting
        
        6. Security Testing
           - Security test cases
           - Vulnerability testing
           - Penetration testing plan
           - Compliance testing
        
        7. Test Automation
           - Automation strategy
           - CI/CD pipeline integration
           - Automated regression testing
           - Continuous monitoring
        
        8. Quality Gates
           - Coverage requirements
           - Performance thresholds
           - Security criteria
           - Code quality metrics
        
        9. Risk Assessment
           - High-risk areas identification
           - Mitigation strategies
           - Contingency plans
        
        10. Resource Planning
            - Team responsibilities
            - Timeline estimates
            - Tool and infrastructure needs
        
        Include specific metrics, tools, and implementation timelines.
        """
        
        try:
            strategy = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(strategy), title="Testing Strategy", border_style="blue")
            console.print(panel)
            
            # Save strategy
            output_file = args.output or "testing_strategy.md"
            file_manager.write_file(output_file, strategy)
            console.print(f"[green]Testing strategy saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Testing strategy creation failed: {e}[/red]")
    
    def analyze_coverage(self, args, gemini_client, file_manager, console):
        """Analyze test coverage and suggest improvements"""
        if not args.input:
            console.print("[red]Error: Coverage report or code file required[/red]")
            return
        
        coverage_data = file_manager.read_file(args.input)
        target_coverage = args.coverage
        console.print("Analyzing test coverage...")
        
        prompt = f"""
        Analyze this test coverage data and provide improvement recommendations:
        
        Coverage Data:
        {coverage_data}
        
        Target Coverage: {target_coverage}%
        
        Please provide:
        1. Coverage Summary
           - Current coverage percentage
           - Coverage by module/file
           - Line coverage analysis
           - Branch coverage analysis
        
        2. Gap Analysis
           - Uncovered code sections
           - Critical paths not tested
           - Edge cases missing
           - Error handling gaps
        
        3. Risk Assessment
           - High-risk uncovered code
           - Business-critical functions
           - Security-sensitive areas
           - Performance-critical sections
        
        4. Improvement Plan
           - Priority test cases to add
           - Specific functions to test
           - Integration test opportunities
           - End-to-end test scenarios
        
        5. Coverage Strategy
           - Achievable coverage targets
           - Timeline for improvements
           - Resource requirements
           - Automation opportunities
        
        6. Quality Metrics
           - Coverage quality assessment
           - Test effectiveness analysis
           - False positive identification
           - Maintenance overhead
        
        7. Recommendations
           - Testing best practices
           - Tool improvements
           - Process optimizations
           - Team training needs
        
        Provide specific, actionable recommendations with priorities.
        """
        
        try:
            coverage_analysis = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(coverage_analysis), title="Coverage Analysis", border_style="cyan")
            console.print(panel)
            
            # Save analysis
            output_file = args.output or "coverage_analysis.md"
            file_manager.write_file(output_file, coverage_analysis)
            console.print(f"[green]Coverage analysis saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Coverage analysis failed: {e}[/red]")
    
    def generate_performance_tests(self, args, gemini_client, file_manager, console):
        """Generate performance and load tests"""
        if not args.input:
            console.print("[red]Error: Code file or API specification required[/red]")
            return
        
        code_content = file_manager.read_file(args.input)
        framework = args.framework or "pytest-benchmark"
        console.print("Generating performance tests...")
        
        prompt = f"""
        Generate comprehensive performance tests for this code:
        
        Code/API to test:
        {code_content}
        
        Testing Framework: {framework}
        
        Please generate:
        1. Performance Test Suite
           - Latency tests
           - Throughput tests
           - Memory usage tests
           - CPU utilization tests
        
        2. Load Testing
           - Normal load scenarios
           - Peak load scenarios
           - Stress testing
           - Endurance testing
        
        3. Benchmark Tests
           - Baseline performance metrics
           - Regression testing
           - Comparative benchmarks
           - Performance thresholds
        
        4. Scalability Tests
           - Horizontal scaling tests
           - Vertical scaling tests
           - Concurrency tests
           - Resource contention tests
        
        5. Memory Profiling
           - Memory leak detection
           - Memory usage patterns
           - Garbage collection impact
           - Memory optimization tests
        
        6. Database Performance
           - Query performance tests
           - Connection pool tests
           - Transaction performance
           - Index effectiveness
        
        7. Network Performance
           - API response time tests
           - Network latency tests
           - Bandwidth utilization
           - Connection handling
        
        8. Monitoring and Reporting
           - Performance metrics collection
           - Alerting thresholds
           - Performance dashboards
           - Trend analysis
        
        Include setup instructions, test data generation, and result interpretation guides.
        Provide specific performance targets and acceptance criteria.
        """
        
        try:
            performance_tests = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(performance_tests), title="Performance Test Suite", border_style="magenta")
            console.print(panel)
            
            # Save tests
            output_file = args.output or "performance_tests.py"
            file_manager.write_file(output_file, performance_tests)
            console.print(f"[green]Performance tests saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Performance test generation failed: {e}[/red]")
    
    def show_detailed_help(self, console):
        """Show detailed help for test command"""
        help_text = """
        # Test Command Help
        
        The test command provides comprehensive testing capabilities including test generation, analysis, and strategy creation.
        
        ## Commands:
        
        ### generate
        Generate comprehensive test suites for your code.
        ```
        ai-engineer test generate --input app.py --framework pytest --type unit --coverage 90
        ```
        
        ### analyze
        Analyze existing test suites for quality and completeness.
        ```
        ai-engineer test analyze --input test_app.py --output test_analysis.md
        ```
        
        ### strategy
        Create comprehensive testing strategy for your project.
        ```
        ai-engineer test strategy --input requirements.md --output testing_strategy.md
        ```
        
        ### coverage
        Analyze test coverage and suggest improvements.
        ```
        ai-engineer test coverage --input . --output coverage_report.md
        ```
        
        ### performance
        Generate performance tests for your application.
        ```
        ai-engineer test performance --input app.py --type load --output perf_tests.py
        ```
        """
        
        panel = Panel(Markdown(help_text), title="Test Command Help", border_style="blue")
        console.print(panel)