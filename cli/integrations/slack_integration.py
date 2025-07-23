"""
Slack integration for codeobit
"""

import requests
from typing import Dict, Any, List

class SlackIntegration:
    """Integration with Slack for team communication and notifications"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json"
        }

    def send_message(self, channel: str, text: str, blocks: List[Dict] = None) -> Dict[str, Any]:
        """Send a message to a Slack channel"""
        url = f"{self.base_url}/chat.postMessage"
        payload = {
            "channel": channel,
            "text": text
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def get_channels(self) -> Dict[str, Any]:
        """Get list of channels"""
        url = f"{self.base_url}/conversations.list"
        
        response = requests.get(url, headers=self.headers)
        return response.json()

    def create_channel(self, name: str, is_private: bool = False) -> Dict[str, Any]:
        """Create a new channel"""
        url = f"{self.base_url}/conversations.create"
        payload = {
            "name": name,
            "is_private": is_private
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def upload_file(self, channels: str, file_path: str, title: str = "", comment: str = "") -> Dict[str, Any]:
        """Upload a file to Slack"""
        url = f"{self.base_url}/files.upload"
        
        with open(file_path, 'rb') as file_content:
            files = {'file': file_content}
            data = {
                'channels': channels,
                'title': title,
                'initial_comment': comment
            }
            headers = {"Authorization": f"Bearer {self.bot_token}"}
            
            response = requests.post(url, headers=headers, files=files, data=data)
            return response.json()

    def send_deployment_notification(self, channel: str, project_name: str, environment: str, status: str, details: str = "") -> Dict[str, Any]:
        """Send a deployment notification with rich formatting"""
        color = "good" if status.lower() == "success" else "danger" if status.lower() == "failed" else "warning"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🚀 Deployment Update*\n*Project:* {project_name}\n*Environment:* {environment}\n*Status:* {status}"
                }
            }
        ]
        
        if details:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:* {details}"
                }
            })
        
        return self.send_message(channel, f"Deployment {status.lower()} for {project_name} in {environment}", blocks)

    def send_build_notification(self, channel: str, project_name: str, build_number: str, status: str, branch: str = "main") -> Dict[str, Any]:
        """Send a build notification"""
        emoji = "✅" if status.lower() == "success" else "❌" if status.lower() == "failed" else "⚠️"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *Build {status}*\n*Project:* {project_name}\n*Build:* #{build_number}\n*Branch:* {branch}"
                }
            }
        ]
        
        return self.send_message(channel, f"Build {status.lower()} for {project_name}", blocks)
