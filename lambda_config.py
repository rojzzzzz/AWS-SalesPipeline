from aws import lambda_client
import zipfile, io
import logging

logger = logging.getLogger(__name__)

LAMBDA_ENDPOINT = 'http://localhost.localstack.cloud:4566'

def create_lambda(name: str, code: str):
    """Helper function to create a lambad with its code"""

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr('handler.py', code)
    buf.seek(0)

    lambda_client.create_function(
        FunctionName=name,
        Runtime='python3.11',
        Role='arn:aws:iam::000000000000:role/pipeline-lambda-role',
        Handler='handler.handler',
        Code={'ZipFile': buf.read()},
        Timeout=300, MemorySize=256,
        Environment={'Variables': {'AWS_ENDPOINT_URL': LAMBDA_ENDPOINT}}
    )

    logger.info(f'Lambda function {name} created successfully.')


create_lambda('validate-fn', """
import json
def handler(event, context):
    key = event['key']
    size = event.get('size', 0)
    errors = []
    if size == 0: errors.append('File is empty')
    if not key.endswith('.csv'): errors.append('File is not a CSV')


    return {'key': key, 'valid': len(errors) == 0, 'errors': errors}
""")

create_lambda('transform-fn', """
import json, csv, io, os, boto3

def handler(event, context):
    s3 = boto3.client('s3', endpoint_url=os.environ.get('AWS_ENDPOINT_URL'))
    key = event['key']
    obj = s3.get_object(Bucket='fashionstore-raw', Key=key)
    content = obj['Body'].read().decode()
    reader = csv.DictReader(io.StringIO(content))
    records = list(reader)
    out_key = key.replace('raw/', '').replace('.csv', '.json')
    s3.put_object(Bucket='fashionstore-processed', Key=out_key, Body='\\n'.join(json.dumps(r) for r in records).encode())
    return {'output_key': out_key, 'records': len(records)}
""")

create_lambda('cataloger-fn', """
import json, boto3, os

def handler(event, context):
    glue = boto3.client('glue', endpoint_url=os.environ.get('AWS_ENDPOINT_URL'))

    columns = [{'Name': 'order_id', 'Type': 'string'}, {'Name': 'customer_id', 'Type': 'string'},
    {'Name': 'product', 'Type': 'string'}, {'Name': 'quantity', 'Type': 'string'},
    {'Name': 'amount', 'Type': 'string'}, {'Name': 'date', 'Type': 'string'}]

    try:
        glue.create_table(
            DatabaseName='fashionstore_prod',
            TableInput={
                'Name': 'sales',
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': {'classification': 'json'},
                'StorageDescriptor': {
                    'Columns': columns,
                    'Location': 's3://fashionstore-processed/orders/',
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hive.hcatalog.data.JsonSerDe'
                    }
                },
            })
    except glue.exceptions.AlreadyExistsException:
        print("Table already exists, skipping creation.")
    

    return {'cataloged': True, 'table': 'sales', 'records': event.get('records', 0)}
""")

create_lambda('notify-fn', """
import json
def handler(event, context):
    print(f"NOTIFICATION: {json.dumps(event)}")
    return {'notified': True}
""")

dispatcher_code = """
import json, os, boto3

def handler(event, context):
    sfn = boto3.client('stepfunctions', endpoint_url=os.environ.get('AWS_ENDPOINT_URL'))
    
    for record in event.get('Records', []):
        key = record['s3']['object']['key']
        size = record['s3']['object']['size']
        sfn.start_execution(
            stateMachineArn='arn:aws:states:us-east-1:000000000000:stateMachine:fashionstore-pipeline',
            input=json.dumps({'key': key, 'size': size, 'bucket': 'fashionstore-raw'})
        )
    return {'dispatched': len(event.get('Records', []))}
"""

create_lambda('dispatcher-fn', dispatcher_code)

logging.info("[OK] All lambda functions created successfully")
