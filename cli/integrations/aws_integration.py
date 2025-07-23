"""
AWS integration for codeobit
"""

import boto3
from typing import Dict, Any

class AWSIntegration:
    """Integration with AWS for cloud resource management"""
    
    def __init__(self, access_key: str, secret_key: str, region_name: str = "us-east-1"):
        self.session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name
        )

    def list_instances(self) -> Dict[str, Any]:
        """List EC2 instances"""
        ec2 = self.session.client('ec2')
        return ec2.describe_instances()

    def create_instance(self, image_id: str, instance_type: str, key_name: str) -> str:
        """Create an EC2 instance"""
        ec2 = self.session.resource('ec2')
        instance = ec2.create_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            KeyName=key_name,
            MinCount=1,
            MaxCount=1
        )
        return instance[0].id
