import json
import logging
from utils.auth import verify_password, generate_token
from utils.db import get_user_by_email
from utils.responses import success, bad_request, unauthorized, server_error

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')

        if not email or not password:
            return bad_request("Email and password are required")

        user = get_user_by_email(email)
        if not user:
            logger.warning(f"Login failed: User {email} not found")
            return unauthorized("Invalid credentials")

        if not verify_password(password, user.get("password")):
            logger.warning(f"Login failed: Incorrect password for {email}")
            return unauthorized("Invalid credentials")

        # Generate JWT
        token = generate_token(email, user.get("role"))
        logger.info(f"User {email} logged in successfully")
        
        return success({"token": token, "email": email, "role": user.get("role")})

    except json.JSONDecodeError:
        return bad_request("Invalid JSON body")
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return server_error()
