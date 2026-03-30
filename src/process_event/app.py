import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """SQS Event Handler"""
    for record in event.get('Records', []):
        try:
            body = json.loads(record.get('body', '{}'))
            # Simulate processing/notification
            event_type = body.get('event')
            email = body.get('email')
            
            if event_type == "UserRegistered":
                logger.info(f"[NOTIFICATION] Sending welcome email to {email}")
            else:
                logger.info(f"Processing unknown event: {body}")
                
        except json.JSONDecodeError:
            logger.error("Failed to decode message body")
        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")
