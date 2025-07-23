"""
GitHub integration for codeobit
"""

import requests
from typing import Dict, Any, List

class GitHubIntegration:
    """Integration with GitHub for repository and collaboration management"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_repositories(self, username: str = None) -> List[Dict[str, Any]]:
        """Get repositories for a user or authenticated user"""
        if username:
            url = f"{self.base_url}/users/{username}/repos"
        else:
            url = f"{self.base_url}/user/repos"
        
        response = requests.get(url, headers=self.headers)
        return response.json()

    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """Create a new repository"""
        url = f"{self.base_url}/user/repos"
        payload = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def create_issue(self, owner: str, repo: str, title: str, body: str = "", labels: List[str] = None) -> Dict[str, Any]:
        """Create an issue in a repository"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        payload = {
            "title": title,
            "body": body,
            "labels": labels or []
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """Get pull requests for a repository"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {"state": state}
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str, body: str = "") -> Dict[str, Any]:
        """Create a pull request"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        payload = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def get_workflow_runs(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get GitHub Actions workflow runs"""
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs"
        
        response = requests.get(url, headers=self.headers)
        return response.json()

    def trigger_workflow(self, owner: str, repo: str, workflow_id: str, ref: str = "main") -> Dict[str, Any]:
        """Trigger a GitHub Actions workflow"""
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
        payload = {"ref": ref}
        
        response = requests.post(url, headers=self.headers, json=payload)
        return {"status": response.status_code, "message": "Workflow triggered successfully" if response.status_code == 204 else "Failed to trigger workflow"}
