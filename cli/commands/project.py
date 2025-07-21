"""
Project management and task tracking commands
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, TaskID

from cli.ai.gemini_client import GeminiClient
from cli.utils.file_manager import FileManager
from cli.models.project import Project, Task, Milestone

class ProjectCommand:
    """Handle project management and task tracking"""
    
    def add_parser(self, subparsers):
        """Add project subcommand parser"""
        parser = subparsers.add_parser('project', help='Project management and task tracking')
        parser.add_argument('action', choices=['init', 'plan', 'tasks', 'timeline', 'status', 'estimate'], 
                          help='Project action to perform')
        parser.add_argument('--name', help='Project name')
        parser.add_argument('--input', '-i', help='Input requirements or project file')
        parser.add_argument('--output', '-o', help='Output project file path')
        parser.add_argument('--template', help='Project template to use')
        parser.add_argument('--duration', help='Project duration estimate')
        parser.add_argument('--team-size', type=int, help='Team size for estimation')
        return parser
    
    def execute(self, args, config_manager, console):
        """Execute project command"""
        console.print(f"[bold blue]Project {args.action.title()}[/bold blue]")
        
        gemini_client = GeminiClient(config_manager.get('api_key'))
        file_manager = FileManager()
        
        if args.action == 'init':
            self.init_project(args, gemini_client, file_manager, console)
        elif args.action == 'plan':
            self.create_project_plan(args, gemini_client, file_manager, console)
        elif args.action == 'tasks':
            self.manage_tasks(args, gemini_client, file_manager, console)
        elif args.action == 'timeline':
            self.create_timeline(args, gemini_client, file_manager, console)
        elif args.action == 'status':
            self.project_status(args, gemini_client, file_manager, console)
        elif args.action == 'estimate':
            self.estimate_project(args, gemini_client, file_manager, console)
    
    def init_project(self, args, gemini_client, file_manager, console):
        """Initialize a new project"""
        project_name = args.name or "New Project"
        template = args.template or "standard"
        
        console.print(f"Initializing project: {project_name}")
        
        # Create project structure
        project_data = {
            "name": project_name,
            "created_date": datetime.now().isoformat(),
            "template": template,
            "status": "initialized",
            "phases": [],
            "tasks": [],
            "milestones": [],
            "team": [],
            "resources": []
        }
        
        # Save project file
        output_file = args.output or f"{project_name.lower().replace(' ', '_')}_project.json"
        file_manager.write_file(output_file, json.dumps(project_data, indent=2))
        
        console.print(f"[green]Project initialized: {output_file}[/green]")
        
        # Display project structure
        table = Table(title=f"Project: {project_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Name", project_name)
        table.add_row("Template", template)
        table.add_row("Status", "Initialized")
        table.add_row("Created", datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        console.print(table)
    
    def create_project_plan(self, args, gemini_client, file_manager, console):
        """Create comprehensive project plan"""
        if not args.input:
            console.print("[red]Error: Requirements input file required[/red]")
            return
        
        requirements = file_manager.read_file(args.input)
        team_size = args.team_size or 3
        duration = args.duration or "3 months"
        
        console.print("Creating comprehensive project plan...")
        
        prompt = f"""
        Create a comprehensive project plan based on these requirements:
        
        Requirements:
        {requirements}
        
        Team Size: {team_size} people
        Target Duration: {duration}
        
        Generate a detailed project plan including:
        
        1. Project Overview:
           - Project scope and objectives
           - Success criteria
           - Key deliverables
           - Assumptions and constraints
        
        2. Project Phases:
           - Phase breakdown with descriptions
           - Phase objectives and deliverables
           - Phase dependencies
           - Duration estimates for each phase
        
        3. Work Breakdown Structure (WBS):
           - Major work packages
           - Task breakdown with descriptions
           - Task dependencies
           - Effort estimates (in hours/days)
           - Resource assignments
        
        4. Timeline and Milestones:
           - Project timeline with key dates
           - Critical milestones
           - Deliverable due dates
           - Review and approval points
        
        5. Resource Planning:
           - Team structure and roles
           - Skill requirements
           - Resource allocation
           - External dependencies
        
        6. Risk Management:
           - Risk identification
           - Risk assessment (probability/impact)
           - Mitigation strategies
           - Contingency plans
        
        7. Quality Assurance:
           - Quality standards
           - Review processes
           - Testing strategy
           - Acceptance criteria
        
        8. Communication Plan:
           - Stakeholder identification
           - Communication channels
           - Meeting schedules
           - Reporting structure
        
        9. Budget Estimation:
           - Resource costs
           - Technology costs
           - External service costs
           - Contingency budget
        
        10. Success Metrics:
            - Key performance indicators
            - Progress tracking methods
            - Quality metrics
            - Success criteria
        
        Format as structured markdown with tables and charts where appropriate.
        Include specific dates, durations, and resource allocations.
        Make it actionable and detailed enough for implementation.
        """
        
        try:
            project_plan = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(project_plan), title="Project Plan", border_style="blue")
            console.print(panel)
            
            # Save project plan
            output_file = args.output or "project_plan.md"
            file_manager.write_file(output_file, project_plan)
            console.print(f"[green]Project plan saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Project plan creation failed: {e}[/red]")
    
    def manage_tasks(self, args, gemini_client, file_manager, console):
        """Manage project tasks"""
        if not args.input:
            console.print("[red]Error: Project plan or requirements required[/red]")
            return
        
        project_info = file_manager.read_file(args.input)
        console.print("Generating task management structure...")
        
        prompt = f"""
        Create a comprehensive task management structure for this project:
        
        Project Information:
        {project_info}
        
        Generate:
        
        1. Task Hierarchy:
           - Epic-level tasks (major features/components)
           - Story-level tasks (user stories/requirements)
           - Sub-tasks (specific implementation tasks)
           - Technical tasks (infrastructure, setup, etc.)
        
        2. Task Details:
           For each task include:
           - Unique task ID
           - Task title and description
           - Acceptance criteria
           - Priority level (High, Medium, Low)
           - Effort estimate (story points or hours)
           - Dependencies (predecessor tasks)
           - Assigned role/skill requirement
           - Labels/tags for categorization
        
        3. Sprint Planning:
           - Sprint structure (2-week sprints recommended)
           - Sprint goals and themes
           - Task allocation per sprint
           - Sprint capacity planning
           - Definition of done
        
        4. Task Categories:
           - Development tasks
           - Testing tasks
           - Documentation tasks
           - DevOps/Infrastructure tasks
           - Research/spike tasks
           - Bug fixes and technical debt
        
        5. Task Dependencies:
           - Dependency mapping
           - Critical path identification
           - Parallel work opportunities
           - Blocking relationships
        
        6. Estimation Framework:
           - Story point scale
           - Estimation guidelines
           - Velocity tracking
           - Effort calibration
        
        7. Task Templates:
           - User story template
           - Bug report template
           - Technical task template
           - Documentation task template
        
        8. Workflow States:
           - Task status workflow
           - Transition criteria
           - Review processes
           - Approval gates
        
        9. Tracking and Metrics:
           - Progress tracking methods
           - Velocity metrics
           - Burndown charts structure
           - Quality metrics
        
        10. Tools Integration:
            - Recommended project management tools
            - Integration workflows
            - Automation opportunities
            - Reporting structures
        
        Format as JSON structure for easy import into project management tools.
        Include markdown documentation for human readability.
        """
        
        try:
            task_structure = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(task_structure), title="Task Management Structure", border_style="green")
            console.print(panel)
            
            # Save task structure
            output_file = args.output or "task_structure.md"
            file_manager.write_file(output_file, task_structure)
            console.print(f"[green]Task structure saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Task management creation failed: {e}[/red]")
    
    def create_timeline(self, args, gemini_client, file_manager, console):
        """Create project timeline"""
        if not args.input:
            console.print("[red]Error: Project plan or task list required[/red]")
            return
        
        project_data = file_manager.read_file(args.input)
        duration = args.duration or "12 weeks"
        console.print("Creating project timeline...")
        
        prompt = f"""
        Create a detailed project timeline based on this information:
        
        Project Data:
        {project_data}
        
        Target Duration: {duration}
        
        Generate:
        
        1. Master Timeline:
           - Project start and end dates
           - Phase timelines with start/end dates
           - Major milestone dates
           - Critical deliverable dates
           - Review and approval dates
        
        2. Sprint Timeline:
           - Sprint planning dates
           - Sprint execution periods
           - Sprint review and retrospective dates
           - Release dates
           - Sprint goals and themes
        
        3. Critical Path Analysis:
           - Critical path tasks
           - Task dependencies and sequence
           - Slack time for non-critical tasks
           - Risk areas for schedule delays
        
        4. Resource Timeline:
           - Team member availability
           - Skill requirement timeline
           - Resource conflicts identification
           - External dependency timeline
        
        5. Deliverable Schedule:
           - Documentation deliverables
           - Code deliverables
           - Testing deliverables
           - Deployment milestones
        
        6. Quality Gates:
           - Code review schedules
           - Testing phases
           - User acceptance testing
           - Security review dates
        
        7. Risk Mitigation Timeline:
           - Risk assessment dates
           - Mitigation implementation
           - Contingency activation points
           - Recovery timelines
        
        8. Communication Schedule:
           - Regular meeting schedule
           - Progress report dates
           - Stakeholder update schedule
           - Demo and presentation dates
        
        9. Buffer and Contingency:
           - Buffer time allocation
           - Contingency plan timelines
           - Schedule risk mitigation
           - Recovery procedures
        
        10. Timeline Visualization:
            - Gantt chart structure (described)
            - Milestone chart
            - Dependency diagram
            - Resource allocation chart
        
        Provide specific dates assuming project starts next Monday.
        Include working days calculation and holiday considerations.
        Format with clear date ranges and dependencies.
        """
        
        try:
            timeline = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(timeline), title="Project Timeline", border_style="cyan")
            console.print(panel)
            
            # Save timeline
            output_file = args.output or "project_timeline.md"
            file_manager.write_file(output_file, timeline)
            console.print(f"[green]Project timeline saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Timeline creation failed: {e}[/red]")
    
    def project_status(self, args, gemini_client, file_manager, console):
        """Generate project status report"""
        if not args.input:
            console.print("[red]Error: Project data file required[/red]")
            return
        
        project_data = file_manager.read_file(args.input)
        console.print("Generating project status report...")
        
        prompt = f"""
        Generate a comprehensive project status report based on this data:
        
        Project Data:
        {project_data}
        
        Create a status report including:
        
        1. Executive Summary:
           - Overall project health (Red/Yellow/Green)
           - Key achievements this period
           - Major issues and risks
           - Next period priorities
        
        2. Progress Summary:
           - Completion percentage by phase
           - Tasks completed vs planned
           - Milestones achieved
           - Deliverables completed
        
        3. Schedule Status:
           - Timeline adherence
           - Delays and their impact
           - Critical path status
           - Schedule risks
        
        4. Budget Status:
           - Budget utilization
           - Cost variance analysis
           - Forecast to completion
           - Budget risks
        
        5. Quality Metrics:
           - Quality gates passed
           - Defect rates
           - Code review metrics
           - Testing progress
        
        6. Team Performance:
           - Team velocity
           - Resource utilization
           - Skill development
           - Team satisfaction
        
        7. Risk and Issues:
           - Active risks
           - New risks identified
           - Issue resolution status
           - Mitigation effectiveness
        
        8. Stakeholder Engagement:
           - Stakeholder feedback
           - Communication effectiveness
           - Change requests
           - Approval status
        
        9. Technical Progress:
           - Architecture implementation
           - Technical debt status
           - Performance metrics
           - Security compliance
        
        10. Recommendations:
            - Course corrections needed
            - Process improvements
            - Resource adjustments
            - Risk mitigation actions
        
        Include specific metrics, percentages, and actionable recommendations.
        Format for executive and technical audiences.
        """
        
        try:
            status_report = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(status_report), title="Project Status Report", border_style="yellow")
            console.print(panel)
            
            # Save status report
            output_file = args.output or f"status_report_{datetime.now().strftime('%Y%m%d')}.md"
            file_manager.write_file(output_file, status_report)
            console.print(f"[green]Status report saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Status report generation failed: {e}[/red]")
    
    def estimate_project(self, args, gemini_client, file_manager, console):
        """Estimate project effort and timeline"""
        if not args.input:
            console.print("[red]Error: Requirements or project specification required[/red]")
            return
        
        requirements = file_manager.read_file(args.input)
        team_size = args.team_size or 3
        console.print("Estimating project effort and timeline...")
        
        prompt = f"""
        Provide comprehensive project estimation based on these requirements:
        
        Requirements:
        {requirements}
        
        Team Size: {team_size} people
        
        Provide estimation for:
        
        1. Effort Estimation:
           - Development effort (person-hours)
           - Testing effort (person-hours)
           - Documentation effort (person-hours)
           - Project management effort (person-hours)
           - Total effort estimate
        
        2. Timeline Estimation:
           - Development timeline
           - Testing timeline
           - Integration timeline
           - Deployment timeline
           - Total project duration
        
        3. Resource Estimation:
           - Required skill sets
           - Team composition recommendations
           - External resource needs
           - Peak resource requirements
        
        4. Technology Estimation:
           - Development stack complexity
           - Infrastructure requirements
           - Third-party service needs
           - Licensing costs
        
        5. Risk-Based Estimation:
           - Best case scenario
           - Most likely scenario
           - Worst case scenario
           - Confidence intervals
        
        6. Phase-wise Breakdown:
           - Requirements analysis phase
           - Design phase
           - Development phase
           - Testing phase
           - Deployment phase
        
        7. Complexity Analysis:
           - Technical complexity rating
           - Business logic complexity
           - Integration complexity
           - UI/UX complexity
        
        8. Estimation Methodology:
           - Estimation technique used
           - Assumptions made
           - Risk factors considered
           - Calibration factors
        
        9. Budget Estimation:
           - Development costs
           - Infrastructure costs
           - Tool and license costs
           - Contingency budget
        
        10. Validation and Calibration:
            - Similar project comparisons
            - Industry benchmarks
            - Historical data considerations
            - Accuracy confidence level
        
        Provide multiple estimation scenarios with justifications.
        Include buffer time and risk mitigation in estimates.
        Use industry-standard estimation techniques.
        """
        
        try:
            estimation = gemini_client.generate_content(prompt)
            
            # Display results
            panel = Panel(Markdown(estimation), title="Project Estimation", border_style="magenta")
            console.print(panel)
            
            # Save estimation
            output_file = args.output or "project_estimation.md"
            file_manager.write_file(output_file, estimation)
            console.print(f"[green]Project estimation saved to: {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Project estimation failed: {e}[/red]")
    
    def show_detailed_help(self, console):
        """Show detailed help for project command"""
        help_text = """
        # Project Command Help
        
        The project command provides comprehensive project management and task tracking capabilities.
        
        ## Commands:
        
        ### init
        Initialize a new project structure.
        ```
        ai-engineer project init --name "My App" --template web --output my_project.json
        ```
        
        ### plan
        Create comprehensive project plan from requirements.
        ```
        ai-engineer project plan --input requirements.md --team-size 5 --duration "4 months"
        ```
        
        ### track
        Track project progress and milestones.
        ```
        ai-engineer project track --input project.json --output progress_report.md
        ```
        
        ### estimate
        Generate project time and cost estimates.
        ```
        ai-engineer project estimate --input requirements.md --output estimation.md
        ```
        """
        
        panel = Panel(Markdown(help_text), title="Project Command Help", border_style="blue")
        console.print(panel)