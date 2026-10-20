from aws import s3, lambda_client
import logging
import json

try:
    lambda_client.add_permission(
        FunctionName='dispatcher-fn',
        StatementId='allow-s3-invoke-dispatcher',
        Action='lambda:InvokeFunction',
        Principal='s3.amazonaws.com',
        SourceArn='arn:aws:s3:::fashionstore-raw',
        SourceAccount='000000000000'
    )
except lambda_client.exceptions.ResourceConflictException:
    logging.warning("Lambda permission already exists for S3 to invoke dispatcher-fn")


s3.put_bucket_notification_configuration(
    Bucket='fashionstore-raw',
    NotificationConfiguration={
        'LambdaFunctionConfigurations': [
            {
                'LambdaFunctionArn': 'arn:aws:lambda:us-east-1:000000000000:function:dispatcher-fn',
                'Events': ['s3:ObjectCreated:*'],
                'Filter': {
                    'Key': {
                        'FilterRules': [
                            {'Name': 'suffix', 'Value': '.csv'}
                        ]
                    }
                }
            }
        ]
    }

)

logging.info("Automatization completed: new file -> pipeline runs")
