import json

def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }

def success(data=None):
    return build_response(200, data or {"message": "Success"})

def bad_request(message="Bad Request"):
    return build_response(400, {"error": message})

def unauthorized(message="Unauthorized"):
    return build_response(401, {"error": message})

def forbidden(message="Forbidden"):
    return build_response(403, {"error": message})

def server_error(message="Internal Server Error"):
    return build_response(500, {"error": message})
