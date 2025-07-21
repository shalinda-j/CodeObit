"""
Security analysis and vulnerability scanning commands
"""

from pathlib import Path
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from cli.ai.gemini_client import GeminiClient
from cli.utils.file_manager import FileManager

class SecurityCommand:
    """Handle security analysis and vulnerability scanning"""
    
    def add_parser(self, subparsers):
        """Add security subcommand parser"""
        parser = subparsers.add_parser('security', help='Security analysis and vulnerability scanning')
        parser.add_argument('action', choices=['scan', 'analyze', 'audit', 'guidelines', 'compliance'], 
                          help='Security action to perform')
        parser.add_argument('--input', '-i', help='Input code file or project directory')
        parser.add_argument('--output', '-o', help='Output report file path')
        parser.add_argument('--standard', help='Security standard (OWASP, NIST, ISO27001)')
        parser.add_argument('--severity', choices=['all', 'high', 'medium', 'low'], 
                          default='all', help='Minimum severity level')
        parser.add_argument('--format', choices=['markdown', 'json', 'csv'], 
                          default='markdown', help='Output format')
        return parser
    
    def execute(self, args, config_manager, console):
        """Execute security command"""
        console.print(f"[bold blue]Security {args.action.title()}[/bold blue]")
        
        gemini_client = GeminiClient(config_manager.get('api_key'))
        file_manager = FileManager()
        
        if args.action == 'scan':
            self.security_scan(args, gemini_client, file_manager, console)
        elif args.action == 'analyze':
            self.security_analyze(args, gemini_client, file_manager, console)
        elif args.action == 'audit':
            self.security_audit(args, gemini_client, file_manager, console)
        elif args.action == 'guidelines':
            self.security_guidelines(args, gemini_client, file_manager, console)
        elif args.action == 'compliance':
            self.compliance_check(args, gemini_client, file_manager, console)
    
    def security_scan(self, args, gemini_client, file_manager, console):
        """Perform comprehensive security scan"""
        if not args.input:
            console.print("[red]Error: Input code file or directory required[/red]")
            return
        
        # Read code content
        if Path(args.input).is_file():
            code_content = file_manager.read_file(args.input)
        else:
            console.print("[yellow]Directory scanning not fully implemented, analyzing individual files[/yellow]")
            # For now, handle as single file
            code_content = file_manager.read_file(args.input)
        
        severity_filter = args.severity
        console.print(f"Scanning for security vulnerabilities (severity: {severity_filter})...")
        
        prompt = f"""
        Perform a comprehensive security vulnerability scan on this code:
        
        Code:
        {code_content}
        
        Severity Filter: {severity_filter}
        
        Scan for these vulnerability categories:
        
        1. OWASP Top 10:
           - Injection vulnerabilities (SQL, NoSQL, LDAP, etc.)
           - Broken authentication and session management
           - Sensitive data exposure
           - XML external entities (XXE)
           - Broken access control
           - Security misconfiguration
           - Cross-site scripting (XSS)
           - Insecure deserialization
           - Using components with known vulnerabilities
           - Insufficient logging and monitoring
        
        2. Input Validation:
           - Input sanitization issues
           - Parameter validation
           - File upload vulnerabilities
           - Command injection
        
        3. Authentication & Authorization:
           - Weak password policies
           - Session management flaws
           - Privilege escalation
           - JWT vulnerabilities
        
        4. Cryptography:
           - Weak encryption algorithms
           - Poor key management
           - Insufficient randomness
           - Hash function vulnerabilities
        
        5. API Security:
           - Rate limiting issues
           - API key exposure
           - Insecure endpoints
           - Data leakage
        
        6. Infrastructure:
           - Hardcoded credentials
           - Configuration issues
           - Dependency vulnerabilities
           - Environment variable exposure
        
        For each vulnerability found, provide:
        - Vulnerability type and category
        - Severity level (Critical, High, Medium, Low)
        - Affected code location (line numbers)
        - Impact description
        - Exploitation scenario
        - Remediation steps
        - CVSS score estimate
        - References to security standards
        
        Format as structured markdown with clear sections and severity indicators.
        """
        
        try:
            scan_results = gemini_client.generate_content(prompt)
            
            # Display results with color coding based on severity
            panel = Panel(Markdown(scan_results), title="Security Scan Results", border_style="red")
            console.print(panel)
            
            # Save scan results
            output_file = args.output or "security_scan_results.md"
            file_manager.write_file(output_file, scan_results)
            console.print(f"[green]Security scan results saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Security scan failed: {e}[/red]")
    
    def security_analyze(self, args, gemini_client, file_manager, console):
        """Analyze code for security best practices"""
        if not args.input:
            console.print("[red]Error: Input code file required[/red]")
            return
        
        code_content = file_manager.read_file(args.input)
        standard = args.standard or "OWASP"
        console.print(f"Analyzing security practices against {standard} standards...")
        
        prompt = f"""
        Analyze this code for security best practices compliance:
        
        Code:
        {code_content}
        
        Security Standard: {standard}
        
        Evaluate compliance with:
        
        1. Secure Coding Practices:
           - Input validation and sanitization
           - Output encoding
           - Error handling and logging
           - Resource management
           - Memory safety
        
        2. Authentication Security:
           - Password handling
           - Session management
           - Multi-factor authentication
           - Account lockout mechanisms
        
        3. Authorization Controls:
           - Access control implementation
           - Privilege separation
           - Role-based access control
           - Permission validation
        
        4. Data Protection:
           - Data encryption at rest and in transit
           - Sensitive data handling
           - Data anonymization
           - PII protection
        
        5. Communication Security:
           - TLS/SSL implementation
           - Certificate validation
           - Secure protocols
           - API security
        
        6. Configuration Security:
           - Secure defaults
           - Configuration management
           - Environment separation
           - Secrets management
        
        7. Logging and Monitoring:
           - Security event logging
           - Audit trails
           - Monitoring implementation
           - Incident detection
        
        8. Dependency Management:
           - Third-party library security
           - Vulnerability management
           - License compliance
           - Supply chain security
        
        For each category, provide:
        - Compliance score (1-10)
        - Issues identified
        - Best practices recommendations
        - Implementation examples
        - Risk assessment
        
        Include specific code improvements and security enhancements.
        """
        
        try:
            analysis = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(analysis), title="Security Analysis Report", border_style="yellow")
            console.print(panel)
            
            # Save analysis
            output_file = args.output or "security_analysis.md"
            file_manager.write_file(output_file, analysis)
            console.print(f"[green]Security analysis saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Security analysis failed: {e}[/red]")
    
    def security_audit(self, args, gemini_client, file_manager, console):
        """Perform comprehensive security audit"""
        if not args.input:
            console.print("[red]Error: Input code or project specification required[/red]")
            return
        
        project_info = file_manager.read_file(args.input)
        standard = args.standard or "OWASP"
        console.print(f"Performing security audit using {standard} framework...")
        
        prompt = f"""
        Perform a comprehensive security audit for this project:
        
        Project Information:
        {project_info}
        
        Audit Framework: {standard}
        
        Provide a complete security audit covering:
        
        1. Executive Summary:
           - Overall security posture
           - Key findings summary
           - Risk level assessment
           - Compliance status
        
        2. Threat Model:
           - Asset identification
           - Threat actor analysis
           - Attack vector mapping
           - Risk scenarios
        
        3. Vulnerability Assessment:
           - Systematic vulnerability analysis
           - Exploitation likelihood
           - Impact assessment
           - Risk prioritization
        
        4. Security Architecture Review:
           - Design security analysis
           - Control effectiveness
           - Architecture weaknesses
           - Defense in depth assessment
        
        5. Code Security Review:
           - Static analysis findings
           - Dynamic analysis recommendations
           - Secure coding compliance
           - Logic flaw identification
        
        6. Infrastructure Security:
           - Network security assessment
           - Server configuration review
           - Cloud security analysis
           - Container security (if applicable)
        
        7. Data Security:
           - Data classification
           - Protection mechanisms
           - Privacy compliance
           - Data lifecycle security
        
        8. Identity and Access Management:
           - Authentication mechanisms
           - Authorization controls
           - User management
           - Privilege management
        
        9. Incident Response:
           - Detection capabilities
           - Response procedures
           - Recovery planning
           - Communication protocols
        
        10. Compliance Assessment:
            - Regulatory compliance
            - Standard adherence
            - Gap analysis
            - Remediation roadmap
        
        11. Recommendations:
            - Priority remediation items
            - Security improvements
            - Process enhancements
            - Training needs
        
        12. Metrics and KPIs:
            - Security metrics
            - Compliance measurements
            - Progress tracking
            - Continuous improvement
        
        Format as a professional audit report with executive summary, detailed findings, and actionable recommendations.
        """
        
        try:
            audit_report = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(audit_report), title="Security Audit Report", border_style="red")
            console.print(panel)
            
            # Save audit report
            output_file = args.output or "security_audit_report.md"
            file_manager.write_file(output_file, audit_report)
            console.print(f"[green]Security audit report saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Security audit failed: {e}[/red]")
    
    def security_guidelines(self, args, gemini_client, file_manager, console):
        """Generate security implementation guidelines"""
        language = args.input or "general"
        standard = args.standard or "OWASP"
        console.print(f"Generating security guidelines for {language} development...")
        
        prompt = f"""
        Generate comprehensive security implementation guidelines:
        
        Target Language/Platform: {language}
        Security Standard: {standard}
        
        Create detailed guidelines covering:
        
        1. Secure Development Lifecycle:
           - Security requirements phase
           - Threat modeling process
           - Secure design principles
           - Implementation best practices
           - Testing methodologies
           - Deployment security
           - Maintenance procedures
        
        2. Input Validation Guidelines:
           - Input validation strategies
           - Sanitization techniques
           - Encoding practices
           - Parameterized queries
           - File upload security
        
        3. Authentication Implementation:
           - Strong authentication methods
           - Password policies
           - Session management
           - Multi-factor authentication
           - Token-based authentication
        
        4. Authorization Best Practices:
           - Access control models
           - Role-based access control
           - Permission systems
           - Privilege escalation prevention
        
        5. Cryptography Guidelines:
           - Encryption standards
           - Key management
           - Hashing algorithms
           - Digital signatures
           - Random number generation
        
        6. Error Handling Security:
           - Secure error messages
           - Logging best practices
           - Information disclosure prevention
           - Exception handling
        
        7. Data Protection:
           - Data classification
           - Encryption requirements
           - Data retention policies
           - Privacy protection
           - Anonymization techniques
        
        8. API Security:
           - API design security
           - Rate limiting
           - Input validation
           - Authentication/authorization
           - API versioning security
        
        9. Database Security:
           - Secure database design
           - Query security
           - Connection security
           - Data access controls
        
        10. Infrastructure Security:
            - Server hardening
            - Network security
            - Container security
            - Cloud security
        
        11. Security Testing:
            - Static analysis
            - Dynamic testing
            - Penetration testing
            - Security test cases
        
        12. Incident Response:
            - Detection mechanisms
            - Response procedures
            - Recovery planning
            - Communication protocols
        
        Include code examples, implementation patterns, and security checklists.
        Provide specific, actionable guidance with technical details.
        """
        
        try:
            guidelines = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(guidelines), title="Security Implementation Guidelines", border_style="blue")
            console.print(panel)
            
            # Save guidelines
            output_file = args.output or f"security_guidelines_{language}.md"
            file_manager.write_file(output_file, guidelines)
            console.print(f"[green]Security guidelines saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Security guidelines generation failed: {e}[/red]")
    
    def compliance_check(self, args, gemini_client, file_manager, console):
        """Check compliance with security standards"""
        if not args.input:
            console.print("[red]Error: Input code or project information required[/red]")
            return
        
        project_info = file_manager.read_file(args.input)
        standard = args.standard or "OWASP"
        console.print(f"Checking compliance with {standard} standards...")
        
        prompt = f"""
        Perform a comprehensive compliance check against {standard} standards:
        
        Project/Code:
        {project_info}
        
        Standard: {standard}
        
        Evaluate compliance for:
        
        1. {standard} Requirements Mapping:
           - Identify applicable requirements
           - Map implementation to requirements
           - Gap analysis
           - Compliance percentage
        
        2. Control Implementation:
           - Administrative controls
           - Technical controls
           - Physical controls
           - Process controls
        
        3. Policy Compliance:
           - Security policies
           - Procedures compliance
           - Documentation requirements
           - Training requirements
        
        4. Risk Management:
           - Risk assessment process
           - Risk treatment
           - Risk monitoring
           - Risk communication
        
        5. Incident Management:
           - Incident response procedures
           - Reporting requirements
           - Evidence handling
           - Recovery procedures
        
        6. Business Continuity:
           - Continuity planning
           - Backup procedures
           - Disaster recovery
           - Testing requirements
        
        7. Vendor Management:
           - Third-party assessments
           - Contract requirements
           - Monitoring procedures
           - Exit strategies
        
        8. Monitoring and Review:
           - Continuous monitoring
           - Regular assessments
           - Management review
           - Improvement processes
        
        For each requirement, provide:
        - Compliance status (Compliant, Partially Compliant, Non-Compliant)
        - Evidence of implementation
        - Gap descriptions
        - Remediation recommendations
        - Priority level
        - Implementation timeline
        
        Generate a compliance scorecard with overall compliance percentage.
        Provide a roadmap for achieving full compliance.
        """
        
        try:
            compliance_report = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(compliance_report), title=f"{standard} Compliance Report", border_style="green")
            console.print(panel)
            
            # Save compliance report
            output_file = args.output or f"compliance_report_{standard.lower()}.md"
            file_manager.write_file(output_file, compliance_report)
            console.print(f"[green]Compliance report saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Compliance check failed: {e}[/red]")
    
    def show_detailed_help(self, console):
        """Show detailed help for security command"""
        help_text = """
        # Security Command Help
        
        The security command provides comprehensive security analysis and vulnerability scanning capabilities.
        
        ## Commands:
        
        ### scan
        Perform vulnerability scanning on code.
        ```
        ai-engineer security scan --input app.py --severity high --output scan_results.md
        ```
        
        ### analyze
        Analyze code for security best practices.
        ```
        ai-engineer security analyze --input app.py --standard OWASP --output analysis.md
        ```
        
        ### audit
        Perform comprehensive security audit.
        ```
        ai-engineer security audit --input . --depth comprehensive --output audit_report.md
        ```
        
        ### compliance
        Check compliance with security standards.
        ```
        ai-engineer security compliance --input . --standard OWASP --output compliance.md
        ```
        """
        
        panel = Panel(Markdown(help_text), title="Security Command Help", border_style="blue")
        console.print(panel)