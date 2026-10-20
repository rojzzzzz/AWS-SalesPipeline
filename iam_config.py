import json
import logging


logger = logging.getLogger(__name__)


def configure_iam(iam):
    trust = json.dumps({"Version": "2012-10-17", "Statement": [
        {"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}
    ]})

    trust_step = json.dumps({"Version": "2012-10-17", "Statement": [
        {'Effect': "Allow", "Principal": {"Service": "states.amazonaws.com"}, "Action": "sts:AssumeRole"}
    ]})

    iam.create_role(RoleName='pipeline-lambda-role', AssumeRolePolicyDocument=trust)
    iam.create_role(RoleName='pipeline-stepfunctions-role', AssumeRolePolicyDocument=trust_step)

    policy_doc = json.dumps({"Version": "2012-10-17", "Statement": [
        {"Effect": "Allow", "Action": ["s3:GetObject"], "Resource": ["arn:aws:s3:::fashionstore-raw/*"]},
        {"Effect": "Allow", "Action": ["s3:PutObject"], "Resource": ["arn:aws:s3:::fashionstore-processed/*"]},
        {"Effect": "Allow", "Action": ["states:StartExecution"], "Resource": ["arn:aws:states:us-east-1:000000000000:stateMachine:fashionstore-pipeline"]},
        {"Effect": "Allow", "Action": ["glue:*"], "Resource": ["*"]},
        {"Effect": "Allow", "Action": ["logs:*"], "Resource": ["*"]},
    ]})

    stepfunctions_policy = json.dumps({
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "lambda:InvokeFunction",
        "Resource": [
            "arn:aws:lambda:us-east-1:000000000000:function:validate-fn",
            "arn:aws:lambda:us-east-1:000000000000:function:transform-fn",
            "arn:aws:lambda:us-east-1:000000000000:function:cataloger-fn",
            "arn:aws:lambda:us-east-1:000000000000:function:notify-fn"
        ]
    }]
    })

    policy = iam.create_policy(PolicyName='pipeline-lambda-policy', PolicyDocument=policy_doc)
    iam.attach_role_policy(RoleName='pipeline-lambda-role', PolicyArn=policy['Policy']['Arn'])

    iam.put_role_policy(RoleName='pipeline-stepfunctions-role',
                        PolicyName='pipeline-stepfunctions-policy',
                        PolicyDocument=stepfunctions_policy)

    logger.info("IAM configured with minimum privileges for Lambda function to run successfully")
