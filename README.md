# PhotoShare – Secure 3‑Tier AWS Photo Sharing App

PhotoShare is a production‑style photo sharing application built to demonstrate how to design a secure, scalable, and modern architecture on AWS. It combines containers, serverless, managed databases, and strong security controls to mimic a real-world cloud system.

## Why This Project Exists

Most demo apps expose databases, hardcode passwords, or ignore monitoring. PhotoShare is intentionally different:

- No public database endpoints  
- No secrets in source code  
- No direct access to S3 objects  
- Built‑in monitoring and alarms  

This makes it a great portfolio project to showcase cloud architecture, not just coding.

## High‑Level Architecture

At a glance, the system is a classic 3‑tier app:

- **Presentation tier** – Users interact via an HTTP endpoint served by an Internet‑facing Application Load Balancer.  
- **Application tier** – A Dockerized web app running on an EC2 instance handles uploads, authentication, and business logic.  
- **Data tier** – A private MySQL RDS instance stores photo metadata and user-related information, completely isolated from the public internet.

All of this runs inside a dedicated VPC with separate public and private subnets.

See `architecture/photoshare-architecture.png` for the full diagram.

## Key AWS Services and Why They’re Used

### VPC, Subnets, and Routing

- **VPC (`photoshare-vpc`)**: Provides an isolated network boundary so the app doesn’t share space with other workloads.  
- **Public subnets**: Host the ALB and EC2 instance, which must be reachable from the internet.  
- **Private subnets**: Host the RDS database so it is never directly accessible from outside.  
- **Internet Gateway + route tables**: Allow only the public subnets to have internet access, keeping the data layer dark.

The goal: strict separation between “what users can reach” and “where sensitive data lives”.

### EC2 + Docker (Application Tier)

- **EC2 (`photoshare-web`)**: Provides a flexible compute layer where Docker can run the web application.  
- **Docker + Docker Compose**: Package the app as a container (`kodekloud/photosharing-app`) so it’s easy to deploy, restart, and port to other environments.

This simulates a real-world pattern: traditional compute hosting a containerized application before moving to ECS/EKS.

### Application Load Balancer (Entry Point)

- **Application Load Balancer (`photoshare-alb`)**:  
  - Acts as the single public entry point.  
  - Terminates incoming HTTP traffic and forwards it to the EC2 instance.  
  - Hides the EC2 instance from direct exposure, which improves security and flexibility (you can later scale to multiple instances).

The ALB also gives you health checks, cleaner URLs, and a place to add HTTPS later.

### RDS MySQL (Data Tier)

- **Amazon RDS MySQL (`photoshare-db`)**:  
  - Managed database (patching, backups, scaling handled by AWS).  
  - Deployed in private subnets with “Public access: No” so it can only be reached from inside the VPC.  

Using a managed DB lets the project focus on architecture and security instead of running a database server manually.

### S3 (Image Storage)

- **S3 bucket (`photoshare-assets-<suffix>`)**:  
  - Stores raw photo files.  
  - Has “Block all public access” enabled so images are not directly fetchable by URL.  

The web app becomes the gatekeeper: users see only the photos they’re allowed to access, even though S3 is the underlying storage.

### Lambda (Background Processing)

- **Lambda function (`photoshare-metadata-extractor`)**:  
  - Triggered automatically when a new object is created in S3.  
  - Reads object metadata (size, MIME type) and sends it to the app via the ALB `/api/webhook` endpoint.  

This decouples heavy or slow work from the user request path, keeping uploads responsive. It also shows how event‑driven patterns work with S3 and Lambda.

### Secrets Manager + KMS (Secret Management)

- **AWS Secrets Manager**:  
  - Stores database credentials (username, password, host, port, dbname) under `photoshare/db/credentials`.  
  - The application reads these at runtime instead of hardcoding them.  

- **KMS (Key Management Service)**:  
  - AWS-managed key `alias/aws/secretsmanager` transparently encrypts the secret at rest.  

Together they solve a common real-world problem: keeping credentials out of code, Git history, and config files.

### IAM Roles and Security Groups (Least Privilege)

- **IAM roles**:  
  - `iam_role_ec2` lets the EC2 instance read from S3 and Secrets Manager, nothing more.  
  - `iam_role_lambda` lets the Lambda function access S3 and write logs to CloudWatch.  

- **Security groups**:  
  - ALB SG allows HTTP from the world and forwards traffic to the web SG.  
  - Web SG allows HTTP only from the ALB SG and SSH for admin access.  
  - DB SG allows MySQL only from the web SG.

Every component gets just enough permission to do its job, which is a key cloud security principle.

### CloudWatch (Monitoring and Reliability)

- **CloudWatch Dashboard (`PhotoShare-Monitor`)**:  
  - Visualizes EC2 CPU usage and Lambda invocations so you can see how the system behaves under load.  

- **CloudWatch Alarm (`PhotoShare-Lambda-Error-Alarm`)**:  
  - Alerts when Lambda errors go above zero, catching silent background failures.  

This turns the architecture from “it works once” into something that can be observed and debugged.

## How the Request Flow Works
- User opens the ALB DNS URL and accesses the PhotoShare UI.

- ALB forwards the request to the Dockerized app on the EC2 instance.

- The app fetches database credentials from Secrets Manager (encrypted with KMS) and connects to the private RDS instance.

- When a photo is uploaded, the app stores the image in the private S3 bucket.

- S3 emits an event that triggers the Lambda function.

- Lambda reads metadata from S3 and POSTs it back to the app via the ALB’s /api/webhook endpoint.

- CloudWatch logs and metrics capture what happened, and alarms fire if Lambda errors occur.

### What This Project Demonstrates
- Designing a secure VPC with public and private subnets

- Applying least‑privilege IAM and security groups

- Running a containerized app on EC2 behind an ALB

- Using serverless (Lambda) for asynchronous processing

- Managing secrets with AWS-native tools (Secrets Manager + KMS)

- Monitoring and alerting with CloudWatch
