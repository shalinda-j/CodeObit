"""
QA command for quality assurance automation and testing
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from cli.commands.base import BaseCommand
from cli.ai.gemini_client import GeminiClient


class QACommand(BaseCommand):
    """Quality assurance automation and testing"""
    
    def add_parser(self, subparsers):
        parser = subparsers.add_parser('qa', help='Quality assurance automation and testing')
        parser.add_argument('--type', choices=['unit', 'integration', 'e2e', 'browser', 'all'], 
                          default='all', help='Type of tests to run')
        parser.add_argument('--file', help='Specific file to test')
        parser.add_argument('--url', help='URL for browser automation testing')
        parser.add_argument('--generate-tests', action='store_true', help='Generate test cases with AI')
        parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
        parser.add_argument('--performance', action='store_true', help='Performance testing')
        return parser
    
    def execute(self, args, config_manager, console):
        """Execute QA command"""
        console.print("[yellow]🧪 Starting QA automation and testing...[/yellow]")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_results': {},
            'coverage': None,
            'performance': None
        }
        
        try:
            if args.generate_tests:
                self.generate_test_cases(args.file, config_manager, console)
            
            if args.type in ['unit', 'all']:
                results['test_results']['unit'] = self.run_unit_tests(console)
            
            if args.type in ['integration', 'all']:
                results['test_results']['integration'] = self.run_integration_tests(console)
            
            if args.type in ['e2e', 'all'] or args.url:
                results['test_results']['e2e'] = self.run_e2e_tests(args.url, console)
            
            if args.type in ['browser', 'all'] or args.url:
                results['test_results']['browser'] = self.run_browser_automation_tests(args.url, console)
            
            if args.coverage:
                results['coverage'] = self.generate_coverage_report(console)
            
            if args.performance:
                results['performance'] = self.run_performance_tests(args.url, console)
            
            # Save QA report
            self.save_qa_report(results)
            
            self.display_qa_summary(console, results)
            
        except Exception as e:
            console.print(f"[red]✗ QA automation failed: {e}[/red]")
    
    def generate_test_cases(self, file_path, config_manager, console):
        """Generate test cases using AI"""
        console.print("[blue]🤖 Generating test cases with AI...[/blue]")
        
        try:
            if file_path and Path(file_path).exists():
                with open(file_path, 'r') as f:
                    code = f.read()
            else:
                # Generate generic test cases for project
                code = "# Project-wide test case generation"
            
            client = GeminiClient()
            prompt = f"""
            As a QA engineer, generate comprehensive test cases for this code:

            ```python
            {code[:2000] if len(code) > 2000 else code}
            ```

            Generate:
            1. Unit tests with pytest
            2. Edge cases and boundary conditions
            3. Error handling tests
            4. Integration test scenarios
            5. Browser automation test scripts (Selenium)
            6. Performance test considerations

            Provide complete, runnable test code.
            """
            
            test_cases = client.generate_content(prompt)
            
            # Save generated test cases
            test_dir = Path("tests/generated")
            test_dir.mkdir(parents=True, exist_ok=True)
            
            test_file = test_dir / f"test_{Path(file_path).stem if file_path else 'project'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            
            with open(test_file, 'w') as f:
                f.write(test_cases)
            
            console.print(f"[green]✓ Test cases generated: {test_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Test generation failed: {e}[/red]")
    
    def run_unit_tests(self, console):
        """Run unit tests"""
        console.print("[blue]Running unit tests...[/blue]")
        
        try:
            result = subprocess.run(['python', '-m', 'pytest', 'tests/', '-v'], 
                                  capture_output=True, text=True, timeout=60)
            
            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': 'Tests timed out after 60 seconds'}
        except FileNotFoundError:
            return {'status': 'skipped', 'message': 'pytest not found - install with: pip install pytest'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def run_integration_tests(self, console):
        """Run integration tests"""
        console.print("[blue]Running integration tests...[/blue]")
        
        try:
            # Look for integration test files
            integration_tests = list(Path("tests").glob("**/test_integration_*.py"))
            
            if not integration_tests:
                return {'status': 'skipped', 'message': 'No integration tests found'}
            
            result = subprocess.run(['python', '-m', 'pytest'] + [str(f) for f in integration_tests] + ['-v'], 
                                  capture_output=True, text=True, timeout=120)
            
            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode,
                'test_files': len(integration_tests)
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def run_e2e_tests(self, url, console):
        """Run end-to-end tests"""
        console.print("[blue]Running E2E tests...[/blue]")
        
        if not url:
            return {'status': 'skipped', 'message': 'No URL provided for E2E tests'}
        
        try:
            # Simple E2E test example
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.get(url)
                
                # Basic E2E checks
                tests = {
                    'page_loads': False,
                    'title_exists': False,
                    'forms_present': False,
                    'links_work': False
                }
                
                # Check if page loads
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                tests['page_loads'] = True
                
                # Check title
                if driver.title and len(driver.title) > 0:
                    tests['title_exists'] = True
                
                # Check forms
                forms = driver.find_elements(By.TAG_NAME, "form")
                if forms:
                    tests['forms_present'] = True
                
                # Check links (first 3)
                links = driver.find_elements(By.TAG_NAME, "a")[:3]
                working_links = 0
                for link in links:
                    href = link.get_attribute('href')
                    if href and href.startswith('http'):
                        working_links += 1
                
                tests['links_work'] = working_links > 0
                
                passed_tests = sum(tests.values())
                total_tests = len(tests)
                
                return {
                    'status': 'passed' if passed_tests == total_tests else 'partial',
                    'tests': tests,
                    'passed': passed_tests,
                    'total': total_tests,
                    'url': url
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def run_browser_automation_tests(self, url, console):
        """Run browser automation tests"""
        console.print("[blue]Running browser automation tests...[/blue]")
        
        if not url:
            return {'status': 'skipped', 'message': 'No URL provided for browser automation'}
        
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                automation_results = []
                
                # Test 1: Page load performance
                start_time = time.time()
                driver.get(url)
                load_time = time.time() - start_time
                automation_results.append({
                    'test': 'page_load_performance',
                    'result': 'passed' if load_time < 5.0 else 'failed',
                    'load_time': load_time
                })
                
                # Test 2: Responsive design check
                driver.set_window_size(1920, 1080)  # Desktop
                desktop_height = driver.execute_script("return document.body.scrollHeight")
                
                driver.set_window_size(375, 667)  # Mobile
                mobile_height = driver.execute_script("return document.body.scrollHeight")
                
                automation_results.append({
                    'test': 'responsive_design',
                    'result': 'passed' if abs(desktop_height - mobile_height) < desktop_height * 0.5 else 'warning',
                    'desktop_height': desktop_height,
                    'mobile_height': mobile_height
                })
                
                # Test 3: Form interaction (if forms exist)
                forms = driver.find_elements(By.TAG_NAME, "form")
                if forms:
                    form = forms[0]
                    inputs = form.find_elements(By.TAG_NAME, "input")
                    if inputs and inputs[0].get_attribute('type') in ['text', 'email']:
                        inputs[0].send_keys("test@example.com")
                        automation_results.append({
                            'test': 'form_interaction',
                            'result': 'passed',
                            'forms_found': len(forms),
                            'inputs_tested': 1
                        })
                
                # Test 4: JavaScript errors
                logs = driver.get_log('browser')
                js_errors = [log for log in logs if log['level'] == 'SEVERE']
                automation_results.append({
                    'test': 'javascript_errors',
                    'result': 'passed' if len(js_errors) == 0 else 'failed',
                    'error_count': len(js_errors),
                    'errors': js_errors[:3]  # First 3 errors only
                })
                
                passed = len([r for r in automation_results if r['result'] == 'passed'])
                total = len(automation_results)
                
                return {
                    'status': 'passed' if passed == total else 'partial',
                    'automation_results': automation_results,
                    'passed': passed,
                    'total': total,
                    'url': url
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def generate_coverage_report(self, console):
        """Generate test coverage report"""
        console.print("[blue]Generating coverage report...[/blue]")
        
        try:
            result = subprocess.run(['python', '-m', 'pytest', '--cov=.', '--cov-report=json', 'tests/'], 
                                  capture_output=True, text=True, timeout=120)
            
            # Try to read coverage report
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                return {
                    'status': 'success',
                    'coverage_percent': coverage_data.get('totals', {}).get('percent_covered', 0),
                    'files_covered': len(coverage_data.get('files', {})),
                    'lines_covered': coverage_data.get('totals', {}).get('covered_lines', 0),
                    'lines_total': coverage_data.get('totals', {}).get('num_statements', 0)
                }
            else:
                return {'status': 'skipped', 'message': 'Coverage report not generated'}
            
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': 'Coverage generation timed out'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def run_performance_tests(self, url, console):
        """Run performance tests"""
        console.print("[blue]Running performance tests...[/blue]")
        
        if not url:
            return {'status': 'skipped', 'message': 'No URL provided for performance testing'}
        
        try:
            import requests
            
            # Performance metrics
            metrics = {}
            
            # Response time test
            response_times = []
            for _ in range(5):
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                response_times.append(end_time - start_time)
                time.sleep(1)
            
            metrics['response_time'] = {
                'average': sum(response_times) / len(response_times),
                'min': min(response_times),
                'max': max(response_times),
                'tests': len(response_times)
            }
            
            # Content size
            metrics['content_size'] = {
                'bytes': len(response.content),
                'kb': len(response.content) / 1024,
                'mb': len(response.content) / (1024 * 1024)
            }
            
            # HTTP status and headers
            metrics['http'] = {
                'status_code': response.status_code,
                'headers_count': len(response.headers),
                'content_type': response.headers.get('content-type', 'unknown')
            }
            
            # Performance scoring
            avg_response = metrics['response_time']['average']
            score = 100
            if avg_response > 3.0:
                score -= 50
            elif avg_response > 1.0:
                score -= 25
            elif avg_response > 0.5:
                score -= 10
            
            return {
                'status': 'completed',
                'performance_score': score,
                'metrics': metrics,
                'url': url
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def save_qa_report(self, results):
        """Save QA report to file"""
        reports_dir = Path("qa_reports")
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def display_qa_summary(self, console, results):
        """Display QA results summary"""
        from rich.table import Table
        from rich.panel import Panel
        
        # Create summary table
        table = Table(title="QA Test Summary")
        table.add_column("Test Type", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")
        
        for test_type, result in results['test_results'].items():
            status = result.get('status', 'unknown')
            status_color = {
                'passed': '[green]PASSED[/green]',
                'failed': '[red]FAILED[/red]',
                'partial': '[yellow]PARTIAL[/yellow]',
                'skipped': '[blue]SKIPPED[/blue]',
                'error': '[red]ERROR[/red]'
            }.get(status, '[gray]UNKNOWN[/gray]')
            
            details = []
            if 'passed' in result and 'total' in result:
                details.append(f"{result['passed']}/{result['total']} passed")
            if 'message' in result:
                details.append(result['message'])
            
            table.add_row(test_type.upper(), status_color, ' | '.join(details))
        
        console.print(table)
        
        # Coverage summary
        if results.get('coverage'):
            coverage = results['coverage']
            if coverage.get('status') == 'success':
                coverage_panel = Panel(
                    f"Coverage: {coverage['coverage_percent']:.1f}%\n"
                    f"Files: {coverage['files_covered']}\n"
                    f"Lines: {coverage['lines_covered']}/{coverage['lines_total']}",
                    title="Code Coverage",
                    border_style="green"
                )
                console.print(coverage_panel)
        
        # Performance summary
        if results.get('performance') and results['performance'].get('status') == 'completed':
            perf = results['performance']
            perf_panel = Panel(
                f"Performance Score: {perf['performance_score']}/100\n"
                f"Avg Response Time: {perf['metrics']['response_time']['average']:.2f}s\n"
                f"Content Size: {perf['metrics']['content_size']['kb']:.1f} KB",
                title="Performance Metrics",
                border_style="blue"
            )
            console.print(perf_panel)