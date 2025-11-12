![CDK build Status](https://github.com/vishalbuilds/CommandCenterLambda/actions/workflows/cdk-ci.yml/badge.svg)
![Python build Status](https://github.com/vishalbuilds/CommandCenterLambda/actions/workflows/python-ci.yml/badge.svg)
![PR validation](https://github.com/vishalbuilds/CommandCenterLambda/actions/workflows/pr-validation-ci.yml/badge.svg)
![Code Coverage](https://codecov.io/gh/vishalbuilds/Command-Center-Lambda/branch/main/graph/badge.svg)
![License](https://img.shields.io/github/license/vishalbuilds/CommandCenterLambda)
![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
[![TypeScript Version](https://img.shields.io/badge/TypeScript-5.x-blue?logo=typescript)](https://www.typescriptlang.org/)
![Last Commit](https://img.shields.io/github/last-commit/vishalbuilds/CommandCenterLambda)

# CommandCenter Lambda

This repository contains the source code and infrastructure definition for the CommandCenterLambda project, a collection of AWS Lambda functions designed for various backend tasks and automations.

## 📖 Overview

The primary use case for this repository is to provide a centralized, scalable, and maintainable solution for serverless business logic. It leverages AWS Lambda for compute, AWS CDK for infrastructure management, and a containerized environment for reliable local development and testing.

## ✨ Features

- **Serverless Architecture**: Built on AWS Lambda for cost-effective and scalable execution.
- **Infrastructure as Code (IaC)**: All AWS resources are defined and managed using the AWS Cloud Development Kit (CDK), ensuring consistency and repeatability.
- **Containerized Development**: Uses Docker/Podman to replicate the Lambda runtime environment locally, allowing for high-fidelity testing before deployment.
- **Modular Structure**: Organized by function, making it easy to add, update, or remove individual components.
- **CI/CD Ready**: Includes placeholders and structure for integrating with continuous integration and deployment pipelines.

## 📂 Project Structure

The repository is organized to separate source code, infrastructure, and test data, promoting a clean and maintainable codebase.

```
CommandCenterLambda/
├── .github/
│   └── workflows/              # GitHub Actions CI/CD workflows
│       ├── cdk-ci.yml
│       ├── lambda-container-ci.yml
│       ├── pr-validation-ci.yml
│       └── python-ci.yml
├── cdk/                        # AWS CDK infrastructure code (TypeScript)
│   ├── bin/
│   │   └── cdk.ts              # CDK App entry point
│   ├── lib/
│   │   ├── iam-role-policies/  # iam role policy defination
|   |   │   ├── connect-policy.ts
|   |   |   ├── s3-policy.ts
|   |   |   └── dynamodb-policy.ts
│   │   ├── iam-role-stack.ts   # iam role stack
│   │   └── lambda-stack.ts     # lambda stack
│   ├── test/                   # CDK tests
│   ├── cdk.json                # CDK configuration
│   ├── package.json            # Node.js dependencies
│   └── README.md               # CDK-specific documentation
├── scripts/
│   └── entry.sh                # Container entry script
├── src/                        # Source code for Lambda functions and utilities
│   ├── common/                 # Shared utilities and models
│   │   ├── client_record/
│   │   ├── constants/
│   │   ├── models/
│   │   └── utils_methods/
│   ├── workflow/               # Lambda function handlers by trigger type
│   │   ├── amazon_connect/
│   │   ├── api_gateway_http/
│   │   ├── api_gateway_rest/
│   │   ├── functional_url/
│   │   └── s3/
│   ├── test_data/              # Sample JSON payloads for testing with fail and pass scenarios
│   │   ├── amazon_connect_workflow/
│   │   ├── s3/
│   │   └── StatusChecker/
│   ├── test_unit/              # Unit tests
│   │   ├── common/
│   │   ├── workflow/
│   │   ├── conftest.py
│   │   └── test_lambda_handler.py
│   ├── lambda_handler.py       # Main Lambda handler entry point
|   ├── requirements.txt        # Python production dependencies
|   └── requirements.dev.txt    # Python python development dependencies
├── .gitignore
├── Dockerfile                  # Dockerfile for building the Lambda container image
├── LICENSE                     # MIT License
└── README.md                   # Repository README

```

## 🚀 AWS CDK Infrastructure

This project uses **AWS CDK v2** to define and provision the cloud infrastructure. The CDK code is located in the `/cdk` directory.

To deploy the infrastructure, you would typically run commands like:

```bash
# Install dependencies
npm install

# Navigate to CDK directory
cd cdk

# Synthesize the CloudFormation template
cdk synth

# Deploy the stack
cdk deploy -c infraVersion=infraVersion-1 -c awsAccount=123456789012 -c region=us-east-1 -c env=dev -c ecrRepositoryArn=arn:aws:ecr:us-east-1:123456789012:repository/Command-Center-Lambda -c imageTag=imageTag
```

## 🧪 Testing

### 1. Run Python Unit Tests

The lambda functions uses `pytest` for unit testing with coverage reporting.

```bash
# Run tests with coverage report
python -m pytest src/test_unit/ --cov=src --cov-report=term-missing --cov-report=html -v

# Run tests without coverage
python -m pytest src/test_unit/ -v

# Run specific test file
python -m pytest src/test_unit/test_lambda_handler.py -v
```

The cdk infrastructure uses `jest` for unit testing with coverage reporting.

### 2. Run Typescript Unit Tests

```bash
# Run all tests with coverage report
npx jest --coverage --coverageReporters="text" --coverageReporters="html" --verbose

# Run tests without coverage
npx jest --verbose

# Run specific test file
npx jest cdk/test/lambda-stack.test.ts --verbose

```

The HTML coverage report will be generated in the `htmlcov/` directory.

## 🛠️ Local Development & Testing

You can build and test the Lambda functions locally using a container, which simulates the AWS Lambda execution environment. This project is configured to use `podman`, but `docker` can also be used.

### Prerequisites

- Git installed
- Docker or Podman installed
- AWS credentials (if testing functions that interact with AWS services)
- curl or any HTTP client for testing

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
# Clone via HTTPS
git clone https://github.com/vishalbuilds/CommandCenterLambda.git

# Or clone via SSH
git clone git@github.com:vishalbuilds/CommandCenterLambda.git

# Navigate to the project directory
cd CommandCenterLambda
```

### 2. Build the Lambda Container

The `Dockerfile` uses a build argument to track build metadata.

#### Build Arguments

| Argument | Required | Default     | Description                       | Example                       |
| -------- | -------- | ----------- | --------------------------------- | ----------------------------- |
| `build`  | No       | `local-dev` | Build identifier/tag for tracking | `local`, `v1.0.0`, `prod-123` |

#### Build Commands

```bash
# Basic build with Docker (build defaults to "local-dev")
docker build -t command-center-lambda .

# Basic build with Podman
podman build -t command-center-lambda .

# Build with custom build tag
docker build --build-arg build=v1.2.3 -t command-center-lambda:v1.2.3 .
```

#### Build for Production (ECR)

```bash
# Build and tag for ECR
docker build \
  --build-arg build=prod-$(date +%Y%m%d-%H%M%S) \
  -t 123456789012.dkr.ecr.us-east-1.amazonaws.com/command-center-lambda:latest .

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/command-center-lambda:latest
```

### 3. Run the Lambda Container

Run the container with AWS credentials and configuration. The container exposes port 8080 internally, which you map to your desired local port (e.g., 9000).

#### Basic Run (without AWS credentials)

```bash
# Using Docker
docker run -p 9000:8080 command-center-lambda

# Using Podman
podman run -p 9000:8080 command-center-lambda
```

#### Run with AWS Credentials and Configuration

For Lambda functions that need to interact with AWS services (S3, DynamoDB, Connect, etc.), pass your AWS credentials and region:

```bash
# Using Docker
docker run -p 9000:8080 \
  -e AWS_ACCESS_KEY_ID=your_access_key_here \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key_here \
  -e AWS_REGION=us-east-1 \
  -e AWS_DEFAULT_REGION=us-east-1 \
  command-center-lambda

# Using Podman
podman run -p 9000:8080 \
  -e AWS_ACCESS_KEY_ID=your_access_key_here \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key_here \
  -e AWS_REGION=us-east-1 \
  -e AWS_DEFAULT_REGION=us-east-1 \
  command-center-lambda
```

#### Run with AWS Session Token (for temporary credentials)

```bash
docker run -p 9000:8080 \
  -e AWS_ACCESS_KEY_ID=your_access_key_here \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key_here \
  -e AWS_SESSION_TOKEN=your_session_token_here \
  -e AWS_REGION=us-east-1 \
  command-center-lambda
```

#### Run with Volume Mount for Test Data

Mount the test data directory to easily access test files from within the container:

```bash
docker run -p 9000:8080 \
  -v $(pwd)/src/test_data:/test_data \
  -e AWS_ACCESS_KEY_ID=your_access_key_here \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key_here \
  -e AWS_REGION=us-east-1 \
  command-center-lambda
```

### 4. Test the Lambda Function

Use `curl` or any API client to send a POST request to the local endpoint, mimicking an AWS Lambda invocation. The test payloads are located in `src/test_data/`.

#### Test with Local File

```bash
# Test Amazon Connect status checker workflow
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d @"src/test_data/amazon_connect_workflow/status_checker_connect_event_pass.json"

# Test S3  status checker workflow
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d @"src/test_data/s3_workflow/status_checker_s3_event_pass.json"
```

#### Test with Inline JSON

```bash
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"key": "value", "test": true}'
```

#### Test with Pretty Output

```bash
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d @"src/test_data/amazon_connect_workflow/status_checker_connect_event_pass.json" | python -m json.tool
```

### 5. Complete Local Testing Workflow

Here's a complete example workflow for local testing:

```bash
# Step 1: Build the image
docker build -t command-center-lambda .

# Step 2: Run the container with AWS credentials
docker run -d -p 9000:8080 \
  --name lambda-test \
  -e AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
  -e AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  -e AWS_REGION=us-east-1 \
  command-center-lambda

# Step 3: Test the function
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d @"src/test_data/StatusChecker/StatusChecker.json"

# Step 4: View container logs
docker logs lambda-test

# Step 5: Stop and remove the container
docker stop lambda-test
docker rm lambda-test
```

### 6. Environment Variables Reference

| Variable                | Required | Default   | Description                                   |
| ----------------------- | -------- | --------- | --------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | No\*     | -         | AWS access key for authentication             |
| `AWS_SECRET_ACCESS_KEY` | No\*     | -         | AWS secret key for authentication             |
| `AWS_SESSION_TOKEN`     | No       | -         | AWS session token (for temporary credentials) |
| `AWS_REGION`            | No       | us-east-1 | AWS region for service calls                  |
| `AWS_DEFAULT_REGION`    | No       | us-east-1 | Default AWS region                            |

\*Required only if your Lambda function interacts with AWS services

## 🔮 Future Plans

- [ ] Implement a full CI/CD pipeline with automated testing and deployment.
- [ ] Expand the collection of Lambda functions to include new features.
- [ ] Single deployment process with config file.
