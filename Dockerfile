FROM public.ecr.aws/lambda/python:3.11

# Install dependencies 
COPY src/requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy application code 
COPY src/ ${LAMBDA_TASK_ROOT}/

# Run unit tests 
RUN python -m pytest ${LAMBDA_TASK_ROOT}/test_unit/ -v --tb=short

# Build arguments and labels
ARG build=local-dev
LABEL build=$build \
      image="command-center-lambda"

# Optional commented RIE block for reference (not needed, as RIE is for local host emulation only)
# RUN if [ ! -f "/usr/local/bin/aws-lambda-rie" ] && [ "$build" == "local-dev" ]; then \
#           echo "Runtime Interface Emulator not found, downloading..." \
#           curl -Lo /usr/local/bin/aws-lambda-rie \
#               https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie \
#           chmod +x /usr/local/bin/aws-lambda-rie \
#           echo "RIE downloaded successfully" \
#       fi \
#       echo "Launching Lambda handler with RIE..."\
#       exec /usr/local/bin/aws-lambda-rie python -m awslambdaric lambda_handler.lambda_handler \
#       echo "RIE launch successfully"

# Environment configuration
ENV PYTHONPATH="${PYTHONPATH}:${LAMBDA_TASK_ROOT}" \
    AWS_REGION="us-east-1" \
    AWS_DEFAULT_REGION="us-east-1"

# Default CMD for Lambda runtime 
CMD ["lambda_handler.lambda_handler"]
