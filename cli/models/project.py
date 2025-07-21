"""
Data models for project management
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator

class TaskStatus(str, Enum):
    """Task status enumeration"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class Priority(str, Enum):
    """Priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProjectStatus(str, Enum):
    """Project status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Task(BaseModel):
    """Task model for project management"""
    id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Detailed task description")
    status: TaskStatus = Field(TaskStatus.TODO, description="Current task status")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority")
    assignee: Optional[str] = Field(None, description="Person assigned to the task")
    estimated_hours: Optional[float] = Field(None, description="Estimated effort in hours")
    actual_hours: Optional[float] = Field(None, description="Actual effort spent in hours")
    story_points: Optional[int] = Field(None, description="Story points for estimation")
    created_date: datetime = Field(default_factory=datetime.now, description="Task creation date")
    due_date: Optional[date] = Field(None, description="Task due date")
    completed_date: Optional[datetime] = Field(None, description="Task completion date")
    dependencies: List[str] = Field(default_factory=list, description="List of dependent task IDs")
    labels: List[str] = Field(default_factory=list, description="Task labels/tags")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")
    comments: List[Dict[str, Any]] = Field(default_factory=list, description="Task comments")
    phase_id: Optional[str] = Field(None, description="Associated phase ID")
    epic_id: Optional[str] = Field(None, description="Associated epic ID")
    
    @validator('estimated_hours', 'actual_hours')
    def validate_hours(cls, v):
        if v is not None and v < 0:
            raise ValueError('Hours must be non-negative')
        return v
    
    @validator('story_points')
    def validate_story_points(cls, v):
        if v is not None and v < 0:
            raise ValueError('Story points must be non-negative')
        return v
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        return (self.due_date is not None and 
                self.status != TaskStatus.DONE and 
                self.due_date < date.today())
    
    def get_progress_percentage(self) -> float:
        """Get task progress as percentage"""
        if self.status == TaskStatus.DONE:
            return 100.0
        elif self.status == TaskStatus.IN_PROGRESS:
            return 50.0
        elif self.status == TaskStatus.IN_REVIEW:
            return 80.0
        else:
            return 0.0

class Milestone(BaseModel):
    """Milestone model for project management"""
    id: str = Field(..., description="Unique milestone identifier")
    title: str = Field(..., description="Milestone title")
    description: Optional[str] = Field(None, description="Milestone description")
    due_date: date = Field(..., description="Milestone due date")
    completed_date: Optional[date] = Field(None, description="Milestone completion date")
    deliverables: List[str] = Field(default_factory=list, description="Expected deliverables")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    associated_tasks: List[str] = Field(default_factory=list, description="Associated task IDs")
    phase_id: Optional[str] = Field(None, description="Associated phase ID")
    is_critical: bool = Field(False, description="Whether this is a critical milestone")
    
    def is_completed(self) -> bool:
        """Check if milestone is completed"""
        return self.completed_date is not None
    
    def is_overdue(self) -> bool:
        """Check if milestone is overdue"""
        return not self.is_completed() and self.due_date < date.today()

class Phase(BaseModel):
    """Phase model for project management"""
    id: str = Field(..., description="Unique phase identifier")
    name: str = Field(..., description="Phase name")
    description: Optional[str] = Field(None, description="Phase description")
    start_date: Optional[date] = Field(None, description="Phase start date")
    end_date: Optional[date] = Field(None, description="Phase end date")
    estimated_duration_weeks: Optional[int] = Field(None, description="Estimated duration in weeks")
    status: ProjectStatus = Field(ProjectStatus.PLANNING, description="Phase status")
    objectives: List[str] = Field(default_factory=list, description="Phase objectives")
    deliverables: List[str] = Field(default_factory=list, description="Expected deliverables")
    prerequisites: List[str] = Field(default_factory=list, description="Phase prerequisites")
    risks: List[Dict[str, Any]] = Field(default_factory=list, description="Associated risks")
    budget_allocated: Optional[float] = Field(None, description="Budget allocated to phase")
    budget_spent: Optional[float] = Field(None, description="Budget spent in phase")
    
    @validator('estimated_duration_weeks')
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Duration must be positive')
        return v
    
    @validator('budget_allocated', 'budget_spent')
    def validate_budget(cls, v):
        if v is not None and v < 0:
            raise ValueError('Budget must be non-negative')
        return v
    
    def get_duration_days(self) -> Optional[int]:
        """Get phase duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        elif self.estimated_duration_weeks:
            return self.estimated_duration_weeks * 7
        return None
    
    def is_active(self) -> bool:
        """Check if phase is currently active"""
        if not self.start_date or not self.end_date:
            return self.status == ProjectStatus.ACTIVE
        
        today = date.today()
        return (self.start_date <= today <= self.end_date and 
                self.status == ProjectStatus.ACTIVE)

class TeamMember(BaseModel):
    """Team member model"""
    id: str = Field(..., description="Unique member identifier")
    name: str = Field(..., description="Member name")
    email: str = Field(..., description="Member email")
    role: str = Field(..., description="Member role")
    skills: List[str] = Field(default_factory=list, description="Member skills")
    availability: float = Field(1.0, description="Availability percentage (0.0 to 1.0)")
    hourly_rate: Optional[float] = Field(None, description="Hourly rate")
    
    @validator('availability')
    def validate_availability(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Availability must be between 0 and 1')
        return v

class Project(BaseModel):
    """Main project model"""
    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: ProjectStatus = Field(ProjectStatus.PLANNING, description="Project status")
    created_date: datetime = Field(default_factory=datetime.now, description="Project creation date")
    start_date: Optional[date] = Field(None, description="Project start date")
    end_date: Optional[date] = Field(None, description="Project end date")
    estimated_duration_weeks: Optional[int] = Field(None, description="Estimated duration in weeks")
    
    # Project organization
    phases: List[Phase] = Field(default_factory=list, description="Project phases")
    tasks: List[Task] = Field(default_factory=list, description="Project tasks")
    milestones: List[Milestone] = Field(default_factory=list, description="Project milestones")
    team_members: List[TeamMember] = Field(default_factory=list, description="Team members")
    
    # Project details
    objectives: List[str] = Field(default_factory=list, description="Project objectives")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    technology_stack: List[str] = Field(default_factory=list, description="Technology stack")
    
    # Budget and resources
    budget_total: Optional[float] = Field(None, description="Total project budget")
    budget_spent: Optional[float] = Field(None, description="Budget spent so far")
    
    # Risk and quality
    risks: List[Dict[str, Any]] = Field(default_factory=list, description="Project risks")
    quality_gates: List[Dict[str, Any]] = Field(default_factory=list, description="Quality gates")
    
    # Configuration
    methodology: str = Field("agile", description="Project methodology")
    template_used: Optional[str] = Field(None, description="Template used for project creation")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Project configuration")
    
    @validator('estimated_duration_weeks')
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Duration must be positive')
        return v
    
    @validator('budget_total', 'budget_spent')
    def validate_budget(cls, v):
        if v is not None and v < 0:
            raise ValueError('Budget must be non-negative')
        return v
    
    def get_total_tasks(self) -> int:
        """Get total number of tasks"""
        return len(self.tasks)
    
    def get_completed_tasks(self) -> int:
        """Get number of completed tasks"""
        return len([task for task in self.tasks if task.status == TaskStatus.DONE])
    
    def get_progress_percentage(self) -> float:
        """Get overall project progress percentage"""
        if not self.tasks:
            return 0.0
        
        total_points = sum(task.story_points or 1 for task in self.tasks)
        completed_points = sum(task.story_points or 1 for task in self.tasks 
                             if task.status == TaskStatus.DONE)
        
        return (completed_points / total_points) * 100 if total_points > 0 else 0.0
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get list of overdue tasks"""
        return [task for task in self.tasks if task.is_overdue()]
    
    def get_active_phase(self) -> Optional[Phase]:
        """Get currently active phase"""
        for phase in self.phases:
            if phase.is_active():
                return phase
        return None
    
    def get_budget_utilization(self) -> float:
        """Get budget utilization percentage"""
        if not self.budget_total or self.budget_total == 0:
            return 0.0
        
        spent = self.budget_spent or 0.0
        return (spent / self.budget_total) * 100
    
    def is_on_schedule(self) -> bool:
        """Check if project is on schedule"""
        if not self.start_date or not self.end_date:
            return True  # Cannot determine if no dates set
        
        total_days = (self.end_date - self.start_date).days
        elapsed_days = (date.today() - self.start_date).days
        
        if elapsed_days <= 0:
            return True  # Project hasn't started yet
        
        expected_progress = (elapsed_days / total_days) * 100
        actual_progress = self.get_progress_percentage()
        
        # Allow 10% variance
        return actual_progress >= (expected_progress - 10)
    
    def get_team_size(self) -> int:
        """Get current team size"""
        return len(self.team_members)
    
    def get_velocity(self) -> float:
        """Calculate team velocity (story points per week)"""
        if not self.start_date:
            return 0.0
        
        weeks_elapsed = max(1, (date.today() - self.start_date).days / 7)
        completed_points = sum(task.story_points or 0 for task in self.tasks 
                             if task.status == TaskStatus.DONE)
        
        return completed_points / weeks_elapsed
    
    def add_task(self, task: Task) -> None:
        """Add a task to the project"""
        self.tasks.append(task)
    
    def add_phase(self, phase: Phase) -> None:
        """Add a phase to the project"""
        self.phases.append(phase)
    
    def add_milestone(self, milestone: Milestone) -> None:
        """Add a milestone to the project"""
        self.milestones.append(milestone)
    
    def add_team_member(self, member: TeamMember) -> None:
        """Add a team member to the project"""
        self.team_members.append(member)
