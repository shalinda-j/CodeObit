"""
External integrations module for codeobit AI Software Engineer CLI
"""

__version__ = "1.0.0"
__author__ = "codeobit Team"

from .jira_integration import JiraIntegration
from .aws_integration import AWSIntegration
from .github_integration import GitHubIntegration
from .slack_integration import SlackIntegration

__all__ = [
    'JiraIntegration',
    'AWSIntegration', 
    'GitHubIntegration',
    'SlackIntegration'
]
