from aws import s3
import logging
import json

logger = logging.getLogger(__name__)

processed = s3.list_objects_v2(Bucket='fashionstore-processed')
logger.info("\nFiles in fashionstore-processed:")

for obj in processed.get('Contents', []):
    logger.info(f"   {obj['Key']} ({obj['Size']} bytes)")

if processed.get('Contents'):
    key = processed['Contents'][0]['Key']
    data = s3.get_object(Bucket='fashionstore-processed', Key=key)
    text = data['Body'].read().decode()
    content = [json.loads(line) for line in text.splitlines() if line.strip()]
    logger.info(f"\nTransformed data ({len(content)} records)")

    for record in content[:3]:
        logger.info(f"   {record}")

