import json
import os
import boto3
import logging
from botocore.exceptions import ClientError
from utils.auth import hash_password
from utils.db import create_user
from utils.responses import success, bad_request, server_error

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client('sqs')

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')
        role = body.get('role', 'user') # Default to 'user'

        if not email or not password:
            return bad_request("Email and password are required")

        if role not in ['user', 'admin']:
            return bad_request("Invalid role. Must be 'user' or 'admin'")

        hashed_pwd = hash_password(password)
        
        user_item = {
            "email": email,
            "password": hashed_pwd,
            "role": role
        }

        created = create_user(user_item)
        if not created:
            return bad_request("User with this email already exists")

        # Send event to SQS
        queue_url = os.environ.get("QUEUE_URL")
        if queue_url:
            message_body = json.dumps({"event": "UserRegistered", "email": email, "role": role})
            sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)
            logger.info(f"Published registration event for {email} to SQS")

        logger.info(f"User registered successfully: {email}")
        return success({"message": "User registered successfully", "email": email, "role": role})

    except json.JSONDecodeError:
        return bad_request("Invalid JSON body")
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return server_error()
