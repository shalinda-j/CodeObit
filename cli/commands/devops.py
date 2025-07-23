"""
DevOps command for CI/CD pipeline management and deployment automation
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.syntax import Syntax

from cli.ai.gemini_client import GeminiClient
from cli.utils.config import ConfigManager
from cli.utils.file_manager import FileManager


class DevOpsCommand:
    """DevOps command for CI/CD pipeline management"""
    
    def __init__(self):
        self.name = "devops"
        self.description = "CI/CD pipeline management and deployment automation"
    
    def add_parser(self, subparsers):
        """Add devops command parser"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Comprehensive DevOps automation including CI/CD pipelines, deployment strategies, and infrastructure management"
        )
        
        subcommands = parser.add_subparsers(dest='devops_action', help='DevOps actions')
        
        # Pipeline command
        pipeline_parser = subcommands.add_parser('pipeline', help='Generate CI/CD pipeline configurations')
        pipeline_parser.add_argument('--platform', choices=['github', 'gitlab', 'azure', 'jenkins'], 
                                   default='github', help='CI/CD platform')
        pipeline_parser.add_argument('--project-type', choices=['web', 'api', 'mobile', 'desktop'], 
                                   default='web', help='Project type')
        pipeline_parser.add_argument('--language', default='python', help='Programming language')
        pipeline_parser.add_argument('--output', help='Output directory for pipeline files')
        
        # Deploy command
        deploy_parser = subcommands.add_parser('deploy', help='Generate deployment configurations')
        deploy_parser.add_argument('--target', choices=['aws', 'azure', 'gcp', 'docker', 'kubernetes'], 
                                 default='docker', help='Deployment target')
        deploy_parser.add_argument('--environment', choices=['dev', 'staging', 'production'], 
                                 default='dev', help='Target environment')
        deploy_parser.add_argument('--project-path', default='.', help='Project root path')
        
        # Infrastructure command
        infra_parser = subcommands.add_parser('infrastructure', help='Generate infrastructure as code')
        infra_parser.add_argument('--provider', choices=['terraform', 'cloudformation', 'pulumi'], 
                                default='terraform', help='IaC provider')
        infra_parser.add_argument('--cloud', choices=['aws', 'azure', 'gcp'], 
                                default='aws', help='Cloud provider')
        infra_parser.add_argument('--services', nargs='+', help='Required cloud services')
        
        # Monitor command
        monitor_parser = subcommands.add_parser('monitor', help='Setup monitoring and alerting')
        monitor_parser.add_argument('--stack', choices=['prometheus', 'datadog', 'newrelic', 'elk'], 
                                  default='prometheus', help='Monitoring stack')
        monitor_parser.add_argument('--metrics', nargs='+', help='Metrics to monitor')
        
        # Security command
        security_parser = subcommands.add_parser('security', help='DevSecOps security integration')
        security_parser.add_argument('--scan-type', choices=['sast', 'dast', 'dependency', 'container'], 
                                   default='sast', help='Security scan type')
        security_parser.add_argument('--tools', nargs='+', help='Security tools to integrate')
        
        return parser
    
    def execute(self, args, config_manager: ConfigManager, console: Console):
        """Execute devops command"""
        try:
            gemini_client = GeminiClient()
            file_manager = FileManager()
            
            if args.devops_action == 'pipeline':
                self.generate_pipeline(args, gemini_client, file_manager, console)
            elif args.devops_action == 'deploy':
                self.generate_deployment(args, gemini_client, file_manager, console)
            elif args.devops_action == 'infrastructure':
                self.generate_infrastructure(args, gemini_client, file_manager, console)
            elif args.devops_action == 'monitor':
                self.setup_monitoring(args, gemini_client, file_manager, console)
            elif args.devops_action == 'security':
                self.setup_security(args, gemini_client, file_manager, console)
            else:
                self.show_detailed_help(console)
                
        except Exception as e:
            console.print(f"[red]DevOps command failed: {e}[/red]")
    
    def generate_pipeline(self, args, gemini_client, file_manager, console):
        """Generate CI/CD pipeline configuration"""
        console.print(f"[blue]🚀 Generating {args.platform} pipeline for {args.project_type} project...[/blue]")
        
        system_instruction = (
            "You are a DevOps engineer expert. Generate comprehensive CI/CD pipeline "
            "configurations that follow best practices for security, efficiency, and reliability. "
            "Include proper testing stages, security scans, and deployment strategies."
        )
        
        prompt = f"""
        Generate a comprehensive CI/CD pipeline configuration for:
        
        Platform: {args.platform}
        Project Type: {args.project_type}
        Language: {args.language}
        
        Include the following pipeline stages:
        1. **Source Control Integration**
           - Trigger conditions (push, PR, tags)
           - Branch protection rules
           - Webhook configurations
        
        2. **Build Stage**
           - Environment setup
           - Dependency installation
           - Build optimization
           - Artifact generation
        
        3. **Testing Stages**
           - Unit tests with coverage
           - Integration tests
           - End-to-end tests
           - Performance tests
        
        4. **Security Scans**
           - SAST (Static Application Security Testing)
           - Dependency vulnerability scanning
           - Container security scanning
           - License compliance checks
        
        5. **Quality Gates**
           - Code quality metrics
           - Coverage thresholds
           - Security scan results
           - Performance benchmarks
        
        6. **Deployment Stages**
           - Development environment
           - Staging environment
           - Production deployment (with approvals)
           - Rollback strategies
        
        7. **Post-Deployment**
           - Health checks
           - Monitoring alerts
           - Notification setup
           - Documentation updates
        
        Provide:
        - Complete pipeline configuration file(s)
        - Setup instructions
        - Best practices recommendations
        - Troubleshooting guide
        
        Make the pipeline production-ready with proper error handling,
        secrets management, and scalability considerations.
        """
        
        try:
            pipeline_config = gemini_client.generate_content(prompt, system_instruction=system_instruction)
            
            # Display pipeline configuration
            panel = Panel(
                Markdown(pipeline_config),
                title=f"🚀 {args.platform.title()} CI/CD Pipeline",
                border_style="blue"
            )
            console.print(panel)
            
            # Save pipeline files
            output_dir = Path(args.output) if args.output else Path(".github/workflows")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine file extension based on platform
            file_extensions = {
                'github': 'yml',
                'gitlab': 'yml', 
                'azure': 'yml',
                'jenkins': 'groovy'
            }
            
            pipeline_file = output_dir / f"ci-cd.{file_extensions.get(args.platform, 'yml')}"
            file_manager.write_file(str(pipeline_file), pipeline_config)
            
            console.print(f"[green]✓ Pipeline configuration saved to: {pipeline_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Pipeline generation failed: {e}[/red]")
    
    def generate_deployment(self, args, gemini_client, file_manager, console):
        """Generate deployment configuration"""
        console.print(f"[blue]🐳 Generating {args.target} deployment for {args.environment} environment...[/blue]")
        
        system_instruction = (
            "You are a cloud infrastructure and deployment expert. Generate production-ready "
            "deployment configurations that follow cloud-native best practices, security standards, "
            "and scalability requirements."
        )
        
        prompt = f"""
        Generate deployment configuration for:
        
        Target Platform: {args.target}
        Environment: {args.environment}
        Project Path: {args.project_path}
        
        Include comprehensive deployment setup:
        
        1. **Container Configuration** (if applicable)
           - Dockerfile optimization
           - Multi-stage builds
           - Security hardening
           - Resource limits
        
        2. **Orchestration** (Kubernetes/Docker Compose)
           - Service definitions
           - ConfigMaps and Secrets
           - Persistent volumes
           - Network policies
        
        3. **Cloud Resources** (if cloud deployment)
           - Compute instances
           - Load balancers
           - Databases
           - Storage solutions
           - Networking (VPC, subnets, security groups)
        
        4. **Configuration Management**
           - Environment-specific configs
           - Secret management
           - Feature flags
           - Application settings
        
        5. **Monitoring & Logging**
           - Health check endpoints
           - Metrics collection
           - Log aggregation
           - Alert configurations
        
        6. **Security**
           - RBAC configurations
           - Network security
           - Secrets encryption
           - Compliance settings
        
        7. **Scaling & Performance**
           - Auto-scaling policies
           - Resource optimization
           - Caching strategies
           - CDN configuration
        
        8. **Backup & Recovery**
           - Data backup strategies
           - Disaster recovery plans
           - Backup schedules
           - Recovery procedures
        
        Provide complete, production-ready configurations with:
        - All necessary configuration files
        - Deployment scripts
        - Environment setup guides
        - Troubleshooting documentation
        """
        
        try:
            deployment_config = gemini_client.generate_content(prompt, system_instruction=system_instruction)
            
            # Display deployment configuration
            panel = Panel(
                Markdown(deployment_config),
                title=f"🐳 {args.target.title()} Deployment Configuration",
                border_style="green"
            )
            console.print(panel)
            
            # Save deployment files
            deploy_dir = Path("deployment") / args.environment
            deploy_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = deploy_dir / f"{args.target}-deployment.md"
            file_manager.write_file(str(config_file), deployment_config)
            
            console.print(f"[green]✓ Deployment configuration saved to: {config_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Deployment generation failed: {e}[/red]")
    
    def generate_infrastructure(self, args, gemini_client, file_manager, console):
        """Generate infrastructure as code"""
        console.print(f"[blue]🏗️ Generating {args.provider} infrastructure for {args.cloud}...[/blue]")
        
        services_list = args.services or ['compute', 'database', 'storage', 'networking']
        
        system_instruction = (
            f"You are an infrastructure as code expert specializing in {args.provider} and {args.cloud}. "
            "Generate well-structured, modular, and reusable infrastructure code that follows "
            "best practices for security, cost optimization, and maintainability."
        )
        
        prompt = f"""
        Generate Infrastructure as Code using {args.provider} for {args.cloud}:
        
        Required Services: {', '.join(services_list)}
        
        Create a comprehensive infrastructure setup including:
        
        1. **Core Infrastructure**
           - VPC/Virtual Networks with subnets
           - Security groups/Network security groups
           - Internet gateways and routing
           - NAT gateways for private subnets
        
        2. **Compute Resources**
           - Auto-scaling groups
           - Load balancers
           - Container orchestration (if needed)
           - Instance templates/VM scale sets
        
        3. **Data Services**
           - Managed databases (RDS, Azure SQL, Cloud SQL)
           - Caching layers (Redis, Memcached)
           - Data warehousing solutions
           - Backup and replication
        
        4. **Storage Solutions**
           - Object storage (S3, Blob Storage, Cloud Storage)
           - File systems
           - Content delivery networks
           - Backup storage
        
        5. **Security & Identity**
           - IAM roles and policies
           - Key management services
           - SSL/TLS certificates
           - Secrets management
        
        6. **Monitoring & Logging**
           - CloudWatch/Azure Monitor/Stackdriver
           - Log analytics
           - Alert management
           - Performance monitoring
        
        7. **DevOps Integration**
           - CI/CD service accounts
           - Deployment automation
           - Environment separation
           - Resource tagging strategy
        
        Provide:
        - Modular {args.provider} code structure
        - Variable definitions and defaults
        - Output definitions
        - README with setup instructions
        - Cost optimization recommendations
        - Security best practices
        
        Make the infrastructure scalable, secure, and cost-effective.
        """
        
        try:
            infrastructure_code = gemini_client.generate_content(prompt, system_instruction=system_instruction)
            
            # Display infrastructure code
            panel = Panel(
                Markdown(infrastructure_code),
                title=f"🏗️ {args.provider.title()} Infrastructure for {args.cloud.upper()}",
                border_style="yellow"
            )
            console.print(panel)
            
            # Save infrastructure files
            infra_dir = Path("infrastructure") / args.cloud
            infra_dir.mkdir(parents=True, exist_ok=True)
            
            infra_file = infra_dir / f"{args.provider}-infrastructure.md"
            file_manager.write_file(str(infra_file), infrastructure_code)
            
            console.print(f"[green]✓ Infrastructure code saved to: {infra_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Infrastructure generation failed: {e}[/red]")
    
    def setup_monitoring(self, args, gemini_client, file_manager, console):
        """Setup monitoring and alerting"""
        console.print(f"[blue]📊 Setting up {args.stack} monitoring stack...[/blue]")
        
        metrics_list = args.metrics or ['cpu', 'memory', 'disk', 'network', 'response_time', 'error_rate']
        
        system_instruction = (
            f"You are a monitoring and observability expert specializing in {args.stack}. "
            "Generate comprehensive monitoring configurations that provide full visibility "
            "into application and infrastructure health, performance, and security."
        )
        
        prompt = f"""
        Setup comprehensive monitoring using {args.stack}:
        
        Metrics to Monitor: {', '.join(metrics_list)}
        
        Create a complete monitoring solution including:
        
        1. **Infrastructure Monitoring**
           - Server/container metrics (CPU, memory, disk, network)
           - Database performance metrics
           - Load balancer metrics
           - Cloud service metrics
        
        2. **Application Monitoring**
           - Application performance metrics (APM)
           - Business metrics and KPIs
           - User experience metrics
           - Error tracking and reporting
        
        3. **Log Management**
           - Centralized logging setup
           - Log parsing and indexing
           - Log retention policies
           - Security event logging
        
        4. **Alerting System**
           - Threshold-based alerts
           - Anomaly detection
           - Alert routing and escalation
           - Notification channels (email, Slack, PagerDuty)
        
        5. **Dashboards**
           - Executive dashboards
           - Operational dashboards
           - Application-specific dashboards
           - Infrastructure dashboards
        
        6. **SLA/SLO Monitoring**
           - Service level indicators
           - Error budgets
           - Availability monitoring
           - Performance targets
        
        7. **Security Monitoring**
           - Security event detection
           - Compliance monitoring
           - Threat detection
           - Audit logging
        
        8. **Capacity Planning**
           - Resource utilization trends
           - Growth predictions
           - Bottleneck identification
           - Cost optimization insights
        
        Provide:
        - Complete monitoring stack configuration
        - Dashboard definitions
        - Alert rule configurations
        - Setup and deployment instructions
        - Best practices guide
        - Troubleshooting documentation
        """
        
        try:
            monitoring_config = gemini_client.generate_content(prompt, system_instruction=system_instruction)
            
            # Display monitoring configuration
            panel = Panel(
                Markdown(monitoring_config),
                title=f"📊 {args.stack.title()} Monitoring Setup",
                border_style="cyan"
            )
            console.print(panel)
            
            # Save monitoring files
            monitoring_dir = Path("monitoring") / args.stack
            monitoring_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = monitoring_dir / "monitoring-setup.md"
            file_manager.write_file(str(config_file), monitoring_config)
            
            console.print(f"[green]✓ Monitoring configuration saved to: {config_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Monitoring setup failed: {e}[/red]")
    
    def setup_security(self, args, gemini_client, file_manager, console):
        """Setup DevSecOps security integration"""
        console.print(f"[blue]🔒 Setting up {args.scan_type} security scanning...[/blue]")
        
        tools_list = args.tools or ['sonarqube', 'snyk', 'owasp-zap', 'clair']
        
        system_instruction = (
            "You are a DevSecOps security expert. Generate comprehensive security "
            "configurations that integrate security throughout the development lifecycle. "
            "Focus on automation, compliance, and proactive threat detection."
        )
        
        prompt = f"""
        Setup DevSecOps security integration:
        
        Scan Type: {args.scan_type}
        Security Tools: {', '.join(tools_list)}
        
        Create comprehensive security integration including:
        
        1. **Static Application Security Testing (SAST)**
           - Code quality and security analysis
           - Vulnerability detection in source code
           - Security rule configurations
           - Integration with CI/CD pipeline
        
        2. **Dynamic Application Security Testing (DAST)**
           - Runtime vulnerability scanning
           - Web application security testing
           - API security testing
           - Penetration testing automation
        
        3. **Dependency Security Scanning**
           - Third-party library vulnerability scanning
           - License compliance checking
           - Dependency update automation
           - Supply chain security
        
        4. **Container Security**
           - Container image scanning
           - Runtime security monitoring
           - Kubernetes security policies
           - Registry security
        
        5. **Infrastructure Security**
           - Infrastructure as Code security scanning
           - Configuration drift detection
           - Compliance monitoring
           - Security benchmarks
        
        6. **Security Policies**
           - Security gate configurations
           - Compliance frameworks (SOC2, GDPR, HIPAA)
           - Security approval workflows
           - Risk assessment automation
        
        7. **Incident Response**
           - Security incident detection
           - Automated response workflows
           - Forensics data collection
           - Recovery procedures
        
        8. **Security Monitoring**
           - Security event correlation
           - Threat intelligence integration
           - Security metrics and KPIs
           - Security dashboard setup
        
        Provide:
        - Security tool configurations
        - Pipeline integration scripts
        - Security policy definitions
        - Incident response playbooks
        - Compliance documentation
        - Security training materials
        """
        
        try:
            security_config = gemini_client.generate_content(prompt, system_instruction=system_instruction)
            
            # Display security configuration
            panel = Panel(
                Markdown(security_config),
                title=f"🔒 DevSecOps Security Setup ({args.scan_type.upper()})",
                border_style="red"
            )
            console.print(panel)
            
            # Save security files
            security_dir = Path("security") / args.scan_type
            security_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = security_dir / "security-setup.md"
            file_manager.write_file(str(config_file), security_config)
            
            console.print(f"[green]✓ Security configuration saved to: {config_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Security setup failed: {e}[/red]")
    
    def show_detailed_help(self, console):
        """Show detailed help for devops command"""
        help_text = """
        # DevOps Command Help
        
        The devops command provides comprehensive CI/CD pipeline management and deployment automation.
        
        ## Commands:
        
        ### pipeline
        Generate CI/CD pipeline configurations for various platforms.
        ```
        codeobit devops pipeline --platform github --project-type web --language python
        codeobit devops pipeline --platform gitlab --project-type api --language nodejs
        ```
        
        ### deploy
        Generate deployment configurations for different targets.
        ```
        codeobit devops deploy --target kubernetes --environment production
        codeobit devops deploy --target aws --environment staging
        ```
        
        ### infrastructure
        Generate Infrastructure as Code configurations.
        ```
        codeobit devops infrastructure --provider terraform --cloud aws --services compute database
        codeobit devops infrastructure --provider pulumi --cloud azure
        ```
        
        ### monitor
        Setup monitoring and alerting systems.
        ```
        codeobit devops monitor --stack prometheus --metrics cpu memory response_time
        codeobit devops monitor --stack datadog --metrics error_rate throughput
        ```
        
        ### security
        Setup DevSecOps security integration.
        ```
        codeobit devops security --scan-type sast --tools sonarqube snyk
        codeobit devops security --scan-type container --tools clair trivy
        ```
        
        ## Integration Examples:
        
        **Complete DevOps Setup:**
        ```bash
        # 1. Generate CI/CD pipeline
        codeobit devops pipeline --platform github --project-type web
        
        # 2. Setup infrastructure
        codeobit devops infrastructure --provider terraform --cloud aws
        
        # 3. Configure monitoring
        codeobit devops monitor --stack prometheus
        
        # 4. Setup security scanning
        codeobit devops security --scan-type sast
        ```
        """
        
        panel = Panel(Markdown(help_text), title="DevOps Command Help", border_style="blue")
        console.print(panel)
