# Architecture

This project implements a secure three‑tier PhotoShare application on AWS.

## High‑Level Design

- **VPC:** `photoshare-vpc` with public subnets (ALB, EC2) and private subnets (RDS).
- **Web tier:** Internet‑facing ALB routes HTTP traffic to a Dockerized EC2 instance.
- **Data tier:** MySQL RDS (`photoshare-db`) in a private subnet, not publicly accessible.
- **Storage:** Private S3 bucket (`photoshare-assets-<suffix>`) for image files.
- **Serverless:** Lambda (`photoshare-metadata-extractor`) triggered by S3 ObjectCreated events to extract metadata and call the app via ALB `/api/webhook`.
- **Security:** IAM roles (`iam_role_ec2`, `iam_role_lambda`), security groups, Secrets Manager + KMS for DB credentials.
- **Observability:** CloudWatch dashboard and alarm for EC2 metrics and Lambda errors.

See `photoshare-architecture.png` in this folder for the full diagram.
