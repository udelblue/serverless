import json
import urllib.parse
#import boto3

def parse_arn(arn):
    # http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
    elements = arn.split(':', 5)
    result = {
        'arn': elements[0],
        'partition': elements[1],
        'service': elements[2],
        'region': elements[3],
        'account': elements[4],
        'resource': elements[5],
        'resource_type': None
    }
    if '/' in result['resource']:
        result['resource_type'], result['resource'] = result['resource'].split('/',1)
    elif ':' in result['resource']:
        result['resource_type'], result['resource'] = result['resource'].split(':',1)
    return result

def info_from_event(event):
    eventname = event['detail']['eventName']
    resources = event['detail']['resources']
    buckets = []
    for r in resources:
        t = r["type"]
        arn = r["ARN"]
        print(t)
        if t == "AWS::S3::Object":
            result = parse_arn(arn)
            objectkey = result['resource']
            bucketname = result['resource_type']
            bucket_item = {'bucketname': bucketname, 'objectkey': objectkey}
            buckets.append(bucket_item)
    results = buckets
    return results
    
def lambda_handler(event, context):
    print("Parse event")   
    result = info_from_event(event)
    print("Loop parse results") 
    if result:
        for b in result:
            bucketname = b['bucketname']
            objectkey = b['ojectkey']

        
    print("End Lambda")   
    return True