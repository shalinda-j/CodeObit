"""
JIRA integration for codeobit
"""

import requests
from typing import Dict, Any

class JiraIntegration:
    """Integration with JIRA for project and issue management"""
    
    def __init__(self, base_url: str, api_token: str, email: str):
        self.base_url = base_url
        self.api_token = api_token
        self.email = email

    def get_project_issues(self, project_key: str) -> Dict[str, Any]:
        """Fetch issues from a JIRA project"""
        url = f"{self.base_url}/rest/api/2/search"
        headers = {
            "Authorization": f"Basic {self.api_token}",
            "Content-Type": "application/json"
        }
        query = {
            "jql": f"project = {project_key} ORDER BY created DESC",
            "maxResults": 50,
            "fields": ["id", "key", "summary", "status", "assignee"]
        }

        response = requests.get(url, headers=headers, params=query)
        return response.json()

    def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Task") -> Dict[str, Any]:
        """Create a new issue in a JIRA project"""
        url = f"{self.base_url}/rest/api/2/issue"
        headers = {
            "Authorization": f"Basic {self.api_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": issue_type
                }
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        return response.json()
