# PhotoShare – Setup Guide

## 1. Prerequisites
- AWS account (us-east-1)
- IAM user with admin or equivalent permissions
- Basic AWS CLI and console knowledge

## 2. Networking
- Create `photoshare-vpc` (10.0.0.0/16)
- Create 4 subnets (Public 1/2, Private 1/2)
- Attach Internet Gateway and create public route table

## 3. IAM
- Role `iam_role_ec2` with S3 + Secrets Manager read
- Role `iam_role_lambda` with Lambda basic + S3

## 4. Data Layer
- KMS key alias `aws/secretsmanager`
- RDS subnet group `photoshare-db-group`
- RDS MySQL instance `photoshare-db` (private, no public access)

## 5. Secrets & Storage
- Secrets Manager secret `photoshare/db/credentials`
- S3 bucket `photoshare-assets-<suffix>` with Block Public Access

## 6. Application Layer
- Security groups: `photoshare-sg` (ALB), `photoshare-web-sg` (EC2), `db-sg` (RDS)
- ALB `photoshare-alb` + target group `photoshare-tg`
- EC2 `photoshare-web` + Docker Compose + `.env`

## 7. Lambda
- Function `photoshare-metadata-extractor`
- Env vars: `S3_BUCKET`, `ALB_DNS`
- S3 trigger: ObjectCreated events

## 8. Monitoring
- CloudWatch dashboard `PhotoShare-Monitor`
- Alarm `PhotoShare-Lambda-Error-Alarm`

## 9. Test
- Open ALB DNS, upload image
- Verify S3 object, Lambda invocation, and DB entry/behavior
