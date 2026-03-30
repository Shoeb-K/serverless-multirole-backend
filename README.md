# Serverless Multi-Role Backend (CDK Python)

This is a robust, production-ready serverless backend demonstrating a "real engineering touch."
It replaces YAML templates (SAM/Serverless Framework) with pure Python using **AWS CDK**.

## Architecture Overview
- **Auth Layer:** Email/Password based JWT Auth using `PyJWT`.
- **Database:** DynamoDB (`UsersTable`) for persisting user data.
- **REST APIs:** Extensively structured API Gateway wrapping AWS Lambdas (`/register`, `/login`, `/users`).
- **Async Events:** `RegisterUser` lambda publishes to SQS, which seamlessly triggers a `ProcessEvent` lambda.

## Directory Structure
```
serverless-multirole-backend/
├── app.py                            # CDK entrypoint
├── infrastructure/
│   └── backend_stack.py              # Pure Python AWS Infrastructure Definition
├── src/
│   ├── register_user/app.py          # POST /register (Creates user and sends SQS)
│   ├── login_user/app.py             # POST /login (Verifies and returns JWT)
│   ├── get_users/app.py              # GET /users (Admin Only - Requires JWT)
│   ├── process_event/app.py          # Async SQS processor
│   ├── utils/                        # Shared Utilities (Dry code)
│   │   ├── auth.py
│   │   ├── db.py
│   │   └── responses.py
│   └── requirements.txt              # Lambda runtime dependencies
├── cdk.json                          # CDK app config
└── requirements.txt                  # CDK deployment dependencies
```

## Setup & Deployment

1. **Install CDK Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Deploy to AWS:**
   Make sure you have valid AWS credentials configured (`aws configure` or exported environment variables), then run:
   ```bash
   cdk deploy
   ```
   CDK will output the API Gateway URL upon successful deployment.

## Design Highlights
- **Strict Role-Based Access Control (RBAC):** `GET /users` enforces proper verification of the `admin` role before responding.
- **Input Validation & Hashing:** Passwords are secure hashed using SHA-256. (Note: Can be swapped for bcrypt but avoids Lambda C-bindings for this demo).
- **Graceful Error Handling:** Dedicated `utils.responses` logic ensuring standard structured JSON returns in all conditions.
- **Microservice Structure:** Code heavily decoupled.
# serverless-multirole-backend
# serverless-multirole-backend
# serverless-multirole-backend
# serverless-multirole-backend
# serverless-multirole-backend
