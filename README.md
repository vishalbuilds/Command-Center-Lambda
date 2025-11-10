![Build Status](https://github.com/vishalbuilds/CommandCenterLambda/actions/workflows/python-src-ci.yml/badge.svg)
![Code Coverage](https://codecov.io/gh/vishalbuilds/CommandCenterLambda/branch/main/graph/badge.svg)
![Linting](https://github.com/vishalbuilds/CommandCenterLambda/actions/workflows/pr-validation-ci.yml/badge.svg)
![License](https://img.shields.io/github/license/vishalbuilds/CommandCenterLambda)
![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![Last Commit](https://img.shields.io/github/last-commit/vishalbuilds/CommandCenterLambda)

# CommandCenter Lambda

This repository contains the source code and infrastructure definition for the CommandCenter project, a collection of AWS Lambda functions designed for various backend tasks and automations.

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
│       ├── lambda-container-ci.yml
│       ├── pr-validation-ci.yml
│       └── python-src-ci.yml
├── cdk/                        # AWS CDK infrastructure code (TypeScript)
│   ├── bin/
│   │   └── cdk.ts              # CDK App entry point
│   ├── lib/                    # CDK stack definitions
│   │   ├── New-bucket-event.ts
│   │   └── remove-pii-s3-stack.ts
│   ├── test/                   # CDK tests
│   ├── cdk.json                # CDK configuration
│   ├── package.json            # Node.js dependencies
│   └── README.md               # CDK-specific documentation
├── scripts/
│   └── entry.sh                # Container entry script
├── src/                        # Source code for Lambda functions
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
│   ├── test_data/              # Sample JSON payloads for testing
│   │   ├── amazon_connect_workflow/
│   │   ├── s3/
│   │   └── StatusChecker/
│   ├── test_unit/              # Unit tests
│   │   ├── common/
│   │   ├── workflow/
│   │   ├── conftest.py
│   │   └── test_lambda_handler.py
│   └── lambda_handler.py       # Main Lambda handler entry point
├── .gitignore
├── Dockerfile                  # Dockerfile for building the Lambda container image
├── LICENSE
├── README.md                   # This file
├── requirements.txt            # Python production dependencies
└── requirements.dev.txt        # Python development dependencies
```

## 🚀 AWS CDK Infrastructure

This project uses **AWS CDK v2** to define and provision the cloud infrastructure. The CDK code is located in the `/cdk` directory.

To deploy the infrastructure, you would typically run commands like:

```bash
# Install dependencies
pip install -r requirements.txt

# Navigate to CDK directory
cd cdk

# Synthesize the CloudFormation template
cdk synth

# Deploy the stack
cdk deploy
```

## 🧪 Testing

This project uses `pytest` for unit testing with coverage reporting.

### Run Unit Tests

```bash
# Run tests with coverage report
python -m pytest src/test_unit/ --cov=src --cov-report=term-missing --cov-report=html -v

# Run tests without coverage
python -m pytest src/test_unit/ -v

# Run specific test file
python -m pytest src/test_unit/test_lambda_handler.py -v
```

The HTML coverage report will be generated in the `htmlcov/` directory.

## 🛠️ Local Development & Testing

You can build and test the Lambda functions locally using a container, which simulates the AWS Lambda execution environment. This project is configured to use `podman`, but `docker` can also be used.

### 1. Build the Lambda Container

The `Dockerfile` is set up to build an image that can run your Lambda function code. The `lambda_handler_env` build argument specifies which function handler to use.

```bash
# Example: Build an image for a specific handler
podman build --build-arg lambda_handler_env=lambda_handler.lambda_handler --build-arg build=local -t lambda-core .
```

### 2. Run the Lambda Container

Run the container, mapping a local port (e.g., 9000) to the container's port 8080.

```bash
podman run -p 9000:8080 lambda-core
```

### 3. Test the Container by Sending a Request

Use `curl` or any API client to send a POST request to the local endpoint, mimicking an AWS Lambda invocation. The test payloads are located in `src/test_data/`.

```bash
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d @"src/test_data/StatusChecker/StatusChecker.json"
```

## 📝 Function Details

1. Function 1
2. Function 2
3. Function 3

### Function 1

Description of Function 1.

### Function 2

Description of Function 2.

### Function 3

Description of Function 3.

## 🔮 Future Plans

- [ ] Implement a full CI/CD pipeline with automated testing and deployment.
- [ ] Add comprehensive unit and integration tests for all functions.
- [ ] Expand the collection of Lambda functions to include new features.
- [ ] Single deployment process with config file.
