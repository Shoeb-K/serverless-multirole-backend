import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

def get_users_table():
    table_name = os.environ.get("TABLE_NAME")
    if not table_name:
        raise ValueError("TABLE_NAME environment variable is not set")
    return dynamodb.Table(table_name)

def get_user_by_email(email: str):
    """Retrieve a user from DynamoDB by email (Primary Key)."""
    table = get_users_table()
    try:
        response = table.get_item(Key={"email": email})
        return response.get("Item")
    except ClientError as e:
        print(f"Error getting user: {e}")
        return None

def create_user(user_item: dict):
    """Create a new user in DynamoDB."""
    table = get_users_table()
    try:
        # ConditionExpression prevents overwriting an existing user with the same email
        table.put_item(
            Item=user_item,
            ConditionExpression="attribute_not_exists(email)"
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return False # User already exists
        raise e

def scan_all_users():
    """Scan all users (For Admin). Note: scanning is expensive in prod."""
    table = get_users_table()
    try:
        response = table.scan()
        # Ensure we don't return passwords
        users = response.get("Items", [])
        for u in users:
            u.pop("password", None)
        return users
    except ClientError as e:
        print(f"Error scanning users: {e}")
        return []
