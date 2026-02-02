import json
import urllib3
import boto3
import os
from urllib.parse import unquote_plus

# Initialize clients outside handler for connection reuse
s3_client = boto3.client('s3')
http = urllib3.PoolManager()


def lambda_handler(event, context):
    # 1. Retrieve Environment Variables
    target_bucket = os.environ.get('S3_BUCKET')
    alb_dns = os.environ.get('ALB_DNS')

    if not target_bucket or not alb_dns:
        print("Error: Missing S3_BUCKET or ALB_DNS environment variables.")
        return False

    # 2. Process S3 Trigger Event
    for record in event['Records']:
        try:
            # Extract and decode object key
            raw_key = record['s3']['object']['key']
            object_key = unquote_plus(raw_key)

            print(f"Processing object: {object_key} from bucket: {target_bucket}")

            # 3. Get System Metadata (Head Object)
            response = s3_client.head_object(Bucket=target_bucket, Key=object_key)

            # Map S3 system metadata to payload
            payload = {
                "objectKey": object_key,
                "fileSize": response.get('ContentLength', 0),
                "mediaType": response.get('ContentType', 'unknown')
            }

            print(f"Extracted Payload: {payload}")

            # 4. Call ALB DNS using urllib3
            clean_dns = alb_dns.replace("http://", "").replace("https://", "").strip("/")
            url = f"http://{clean_dns}/api/webhook"

            encoded_data = json.dumps(payload).encode('utf-8')

            req = http.request(
                "POST",
                url,
                body=encoded_data,
                headers={"Content-Type": "application/json"},
                retries=False
            )

            print(f"ALB Response Status: {req.status}")
            print(f"ALB Response Body: {req.data.decode('utf-8')}")

        except Exception as e:
            print(f"Error processing object {object_key}: {str(e)}")
            raise e

    return {
        "statusCode": 200,
        "body": json.dumps("Metadata processing complete")
    }
