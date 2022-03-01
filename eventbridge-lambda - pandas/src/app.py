import os
from io import StringIO
from io import BytesIO
import boto3
import pandas as pd
from datetime import date

todays_date = date.today()
sink_bucket = os.environ['SINK_BUCKET']
sink_prefix = os.environ['SINK_PREFIX']
s3_client = boto3.client('s3')



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

def parse_event(event):
    eventname = event['detail']['eventName']
    resources = event['detail']['resources']
    buckets = []
    for r in resources:
        t = r["type"]
        arn = r["ARN"]
        if t == "AWS::S3::Object":
            result = parse_arn(arn)
            objectkey = result['resource']
            bucketname = result['resource_type']
            filename = objectkey.rsplit("/", 1)[-1]
            fileextention = filename.rsplit(".", 1)[-1]
            cleanfilename = filename.rsplit(".", 1)[0]
            bucket_item = {'bucketname': bucketname, 'objectkey': objectkey, 'filename' : filename, 'cleanfilename': cleanfilename, 'extention' : fileextention}
            buckets.append(bucket_item)
    results = buckets
    return results

def lambda_handler(event, context):
    
    try:
        print("Parse event")   
        results = parse_event(event)
        print("Loop parse results") 
        if results:
            for b in results:
                bucketname = b['bucketname']
                objectkey = b['objectkey']
                filename = b['filename']
                extention = b['extention']
                cleanfilename = b['cleanfilename']
                #Getting object from bucket
                print( "bucketname:" + str(bucketname) + ", object:" + str(objectkey) + ", filename:" + str(filename) + ", extention:" + str(extention)  )
                source_obj = s3_client.get_object(Bucket=bucketname, Key=objectkey)

                print("Loading Begins")
                #loading file
                sink_body = ""
                df_s3_data = pd.DataFrame()
                if extention == 'csv':
                    print("csv")
                    df_s3_data = pd.read_csv(BytesIO(source_obj['Body'].read()), encoding='utf8')
                    print("loaded in dataframe")

                elif extention == 'json':
                    print("json")
                    df_s3_data = pd.read_json(BytesIO(source_obj['Body'].read()), encoding='utf8')
                elif extention == 'parquet':
                    print("parquet")
                    df_s3_data = pd.read_parquet(BytesIO(source_obj['Body'].read()), encoding='utf8')
                elif extention == "xlsx":
                    print("excel")
                    df_s3_data = pd.read_excel(BytesIO(source_obj['Body'].read()), encoding='utf8')
                else:
                    print(extention + " is an unknown file type.")
                print("Transformation Begins")
                
                
                df_s3_data['test file name'] = "test.csv"
                print(df_s3_data.head(n=10).to_string(index=False))


                print("Transformation Ends")
                #sink_txtdata = source_objbody
                sinkfileextention = "csv"
                #Filename is year/month/day/filename
                sink_filename = str(todays_date.year) +"/"+ str(todays_date.month) + "/" + str(todays_date.day) + "/" + cleanfilename + "." + sinkfileextention
                print("Writing Object")
                with StringIO() as string_buffer:
                    df_s3_data.to_csv(string_buffer, index=False)
                    key = sink_prefix + sink_filename 
                    response = s3_client.put_object( Bucket= sink_bucket, Key= key, Body= string_buffer.getvalue())
                    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
                    if status == 200:
                        print(f"Successful S3 put_object response. Status - {status}")
                        print("Write Object Complete: " + sink_bucket + "/" + key)
                    else:
                        print(f"Unsuccessful S3 put_object response. Status - {status}")
        
        print("End Lambda")
        return True
    except Exception as err:
        print(err)
        return True