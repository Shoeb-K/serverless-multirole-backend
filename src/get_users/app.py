import logging
import jwt
from utils.auth import extract_token, decode_token
from utils.db import scan_all_users
from utils.responses import success, unauthorized, forbidden, server_error

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        headers = event.get('headers', {})
        token = extract_token(headers)
        
        if not token:
            return unauthorized("Missing or invalid Authorization header")

        try:
            payload = decode_token(token)
            role = payload.get("role")
            
            if role != "admin":
                logger.warning(f"Access denied for user {payload.get('email')}. Role: {role}")
                return forbidden("Admin access required")
                
        except jwt.ExpiredSignatureError:
            return unauthorized("Token expired")
        except jwt.InvalidTokenError:
            return unauthorized("Invalid token")

        # Fetch all users
        users = scan_all_users()
        logger.info(f"Admin {payload.get('email')} retrieved user list")
        
        return success({"users": users})

    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return server_error()
