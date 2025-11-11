#!/bin/sh
set -e

# Get lambda handler from environment variable
lambda_handler="${lambda_handler:-lambda_handler.lambda_handler}"

if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
    echo "🟢 Starting in LOCAL mode using Lambda RIE (listening on :8080)..."

    # Ensure RIE binary exists
    if [ ! -f "/aws-lambda-rie" ]; then
        echo "⚠️  Runtime Interface Emulator not found, downloading..."
        curl -Lo /aws-lambda-rie https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie
        chmod +x /aws-lambda-rie
    fi

    # Run RIE in API server mode (accepting curl -d events)
    exec /aws-lambda-rie python -m awslambdaric "$lambda_handler"

else
    echo "🚀 Starting in AWS cloud mode using lambda runtime interface directly"
    exec python3 -m awslambdaric "$lambda_handler"
fi
