from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    Duration,
    RemovalPolicy
)
from constructs import Construct

class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Create DynamoDB Table
        users_table = dynamodb.Table(
            self, "UsersTable",
            partition_key=dynamodb.Attribute(name="email", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY # Note: For prod use RETAIN
        )

        # 2. Create SQS Queue
        event_queue = sqs.Queue(
            self, "EventDrivenQueue",
            visibility_timeout=Duration.seconds(30)
        )

        # Common Lambda Environment/Settings
        lambda_env = {
            "TABLE_NAME": users_table.table_name,
            "QUEUE_URL": event_queue.queue_url,
            "JWT_SECRET": "your-256-bit-secret" # In prod, fetch from Secrets Manager
        }

        # 3. Create Lambdas
        # Register User Lambda
        register_lambda = _lambda.Function(
            self, "RegisterUserFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="register_user.app.handler",
            code=_lambda.Code.from_asset("src", bundling={
                "image": _lambda.Runtime.PYTHON_3_11.bundling_image,
                "command": [
                    "bash", "-c", "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"
                ]
            }),
            environment=lambda_env
        )
        
        # Login User Lambda
        login_lambda = _lambda.Function(
            self, "LoginUserFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="login_user.app.handler",
            code=_lambda.Code.from_asset("src", bundling={
                "image": _lambda.Runtime.PYTHON_3_11.bundling_image,
                "command": [
                    "bash", "-c", "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"
                ]
            }),
            environment=lambda_env
        )

        # Get Users Lambda
        get_users_lambda = _lambda.Function(
            self, "GetUsersFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="get_users.app.handler",
            code=_lambda.Code.from_asset("src", bundling={
                "image": _lambda.Runtime.PYTHON_3_11.bundling_image,
                "command": [
                    "bash", "-c", "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"
                ]
            }),
            environment=lambda_env
        )

        # Process Event Lambda
        process_event_lambda = _lambda.Function(
            self, "ProcessEventFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="process_event.app.handler",
            code=_lambda.Code.from_asset("src")
        )

        # 4. Event Source Mapping
        # We need to use aws_lambda_event_sources
        from aws_cdk.aws_lambda_event_sources import SqsEventSource
        process_event_lambda.add_event_source(SqsEventSource(event_queue, batch_size=10))

        # 5. Grant Permissions
        users_table.grant_read_write_data(register_lambda)
        users_table.grant_read_data(login_lambda)
        users_table.grant_read_data(get_users_lambda)
        
        event_queue.grant_send_messages(register_lambda)
        event_queue.grant_consume_messages(process_event_lambda)

        # 6. API Gateway Configuration
        # API Gateway
        api = apigw.RestApi(
            self, "MultiRoleBackendApi",
            rest_api_name="Multi-Role Backend Service",
            description="This service handles user registration, login and admin listing."
        )

        # POST /register
        register_integration = apigw.LambdaIntegration(register_lambda)
        api.root.add_resource("register").add_method("POST", register_integration)

        # POST /login
        login_integration = apigw.LambdaIntegration(login_lambda)
        api.root.add_resource("login").add_method("POST", login_integration)

        # GET /users
        get_users_integration = apigw.LambdaIntegration(get_users_lambda)
        api.root.add_resource("users").add_method("GET", get_users_integration)
