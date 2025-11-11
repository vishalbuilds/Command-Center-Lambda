FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy scripts and give access
COPY scripts/test_runner.sh scripts/lambda_entry.sh /
RUN chmod +x /test_runner.sh /lambda_entry.sh

# Copy application code (most frequent changes)
COPY src/ ${LAMBDA_TASK_ROOT}/

# Run tests
RUN /test_runner.sh

# Build arguments and labels
ARG build=local-dev
LABEL build=$build \
      image="command-center-lambda"

# Environment configuration
ENV PYTHONPATH="${PYTHONPATH}:${LAMBDA_TASK_ROOT}" \
    lambda_handler="lambda_handler.lambda_handler" \
    AWS_REGION="us-east-1" \
    AWS_DEFAULT_REGION="us-east-1"

ENTRYPOINT ["/lambda_entry.sh"]