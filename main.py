from iam_config import configure_iam
from orchestration import pipeline
from ingestion import ingestion
from aws import s3, iam, glue, sfn
import logging
import json
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


for bucket in ['fashionstore-raw', 'fashionstore-processed', 'fashionstore-athena-results']:
    s3.create_bucket(Bucket=bucket)
    logging.info(f"[OK] Bucket {bucket} successfully created")


try:
    glue.create_database(DatabaseInput={'Name': 'fashionstore_prod'})
except glue.exceptions.AlreadyExistsException:
    logging.info("[OK] Database fashionstore_prod already exists")
else:
    logging.info(f"[OK] Database fashionstore_prod successfully created")

configure_iam(iam)

import lambda_config

sfn.create_state_machine(
    name='fashionstore-pipeline',
    definition=json.dumps(pipeline),
    roleArn='arn:aws:iam::000000000000:role/pipeline-stepfunctions-role'
)
logging.info("[OK] Pipeline Step Functions created successfully")

ingestion()

execution = sfn.start_execution(
    stateMachineArn='arn:aws:states:us-east-1:000000000000:stateMachine:fashionstore-pipeline',
    input=json.dumps({
        "key": "orders/2024-01-15/orders_hour_14.csv",
        "size": 1024,
        "bucket": "fashionstore-raw"
    })
)
logger.info(f"Running pipeline: {execution['executionArn'].split(':')[-1]}")

while True:
    desc = sfn.describe_execution(executionArn=execution['executionArn'])
    if desc['status'] != 'RUNNING':
        break

    time.sleep(1)

status = desc['status']
if status == 'SUCCEEDED':
    logger.info("Pipeline execution completed successfully.")
else:
    logger.error(f"Pipeline execution failed with status: {status}")

if 'output' in desc:
    logger.info(f"Pipeline output: {desc['output']}")

import notifications
