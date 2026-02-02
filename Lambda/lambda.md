# photoshare-metadata-extractor (Lambda)

This Lambda function is triggered by S3 ObjectCreated events from the `photoshare-assets-<suffix>` bucket. It reads the uploaded object’s metadata and sends a JSON payload to the PhotoShare app through the ALB.

## Responsibilities

- Read `S3_BUCKET` and `ALB_DNS` from environment variables.
- For each S3 event record:
  - Extract the object key.
  - Call `HeadObject` on S3 to get `ContentLength` and `ContentType`.
  - Build a JSON payload: `objectKey`, `fileSize`, `mediaType`.
  - POST the payload to `http://<ALB_DNS>/api/webhook` using `urllib3`.

## Configuration

- Runtime: Python 3.x  
- IAM Role: `iam_role_lambda` with `AmazonS3FullAccess` and `AWSLambdaBasicExecutionRole`.  
- Trigger: S3 bucket `photoshare-assets-<suffix>` on **All object create events**.  
- Env vars:
  - `S3_BUCKET` = your bucket name  
  - `ALB_DNS` = your ALB DNS name (without protocol)

