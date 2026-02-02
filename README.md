# PhotoShare – Secure 3‑Tier AWS Photo Sharing App

PhotoShare is a secure three‑tier photo sharing application on AWS that uses a VPC with public and private subnets, an Internet‑facing Application Load Balancer, a Dockerized EC2 web server, a private MySQL RDS database, S3 for image storage, Lambda for metadata processing, and CloudWatch for monitoring.

## Architecture Highlights

- **Networking (VPC)**: Custom VPC (`photoshare-vpc`) with public subnets for ALB + EC2 and private subnets for RDS, ensuring the database is never directly exposed to the internet.
- **Security**:
  - IAM roles `iam_role_ec2` and `iam_role_lambda` for least‑privilege access (no hardcoded credentials).
  - Security groups isolate web tier and DB tier; RDS only accessible from the web server SG.
  - Secrets Manager + KMS (`alias/aws/secretsmanager`) for encrypted DB credentials.
- **Data Layer**:
  - Amazon RDS MySQL (`photoshare-db`) in private subnets via DB subnet group (`photoshare-db-group`).
  - Database is non‑public (Public Access = No) with an initial schema `photoshare`.
- **Storage & Serverless**:
  - Private S3 bucket (`photoshare-assets-<suffix>`) with “Block all public access” enabled and default AES‑256 encryption.
  - Lambda function (`photoshare-metadata-extractor`) triggered on S3 ObjectCreated events to extract image metadata and POST it to the app via ALB DNS.
- **Application Layer**:
  - EC2 instance (`photoshare-web`) in public subnet running Docker Compose.
  - Container image: `kodekloud/photosharing-app`, exposing port 80 via `docker-compose.yml`.
  - `.env` pulls S3 bucket name and Secrets Manager secret name at runtime.
- **Observability**:
  - CloudWatch dashboard (`PhotoShare-Monitor`) tracking EC2 CPU and Lambda invocations.
  - CloudWatch alarm (`PhotoShare-Lambda-Error-Alarm`) on Lambda errors > 0.

## Repository Structure

- `architecture/` – Architecture diagram and high‑level design docs.
- `lambda/` – Lambda source code and configuration notes.
- `docs/` – Detailed setup guide, commands, and troubleshooting notes.
- `screenshots/` – UI, AWS console, and monitoring screenshots.
- `infra/` (optional) – Infrastructure as Code (Terraform/CloudFormation) if added later.

## How It Works (Flow)

1. User accesses the app via the ALB DNS.
2. ALB routes HTTP traffic to the EC2 web server in the public subnet.
3. The app retrieves DB credentials from Secrets Manager (encrypted with KMS) and connects to the MySQL RDS instance in the private subnet.
4. When a user uploads a photo, the app stores the image in the private S3 bucket.
5. S3 ObjectCreated event triggers the Lambda function, which:
   - Reads object metadata from S3.
   - Sends metadata via HTTP POST to the app through the ALB `/api/webhook` endpoint.
6. CloudWatch tracks EC2 CPU, Lambda invocations, and raises an alarm if Lambda errors occur.

## Future Enhancements

- Add Auto Scaling Group for the web tier.
- Add HTTPS via ACM and Route 53 custom domain.
- Convert manual setup to full Infrastructure as Code (CloudFormation/Terraform/CDK).

