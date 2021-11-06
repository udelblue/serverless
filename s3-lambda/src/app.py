import os
import json
import logging
import boto3
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def lambda_handler(event, context):
    logger.info("Start")
    
    # retrieve bucket name and file_key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    logger.info('Reading {} from {}'.format(file_key, bucket_name))

    # get the object
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)

    # get file content
    content = obj['Body'].read().decode("utf-8")

    # Transformtion logic
    logger.info('transform logic')
    # Transformtion logic end

    # get destination bucketname
    destination_bucket = os.environ.get('DESTINATION_BUCKETNAME')

    # write to destination bucket
    logger.info("Record built, writing to file")
    key = "{}_{}.json".format(file_key , time.time())

    response = s3.put_object(
        Bucket=destination_bucket,
        Key=key,
        Body=content
    )

    logger.info("Completed parsing")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Job complete')
    }