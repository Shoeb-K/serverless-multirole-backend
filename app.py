#!/usr/bin/env python3
import os
import aws_cdk as cdk
from infrastructure.backend_stack import BackendStack

app = cdk.App()
BackendStack(app, "ServerlessMultiRoleBackendStack")

app.synth()
